#!/usr/bin/env python3
"""
YouTube Influencer Finder (robust)
- Keyword search for channels
- Safe stats + fallbacks to ensure we pull some data
- Handles missing uploads playlists by falling back to search-by-channel videos
- Retries on transient errors
- Exports CSV
"""

import os
import csv
import time
import math
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ----------------------------
# Config
# ----------------------------
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Backoff/retry
MAX_RETRIES = 4
BASE_SLEEP = 0.8  # seconds

# Per-call pacing (be polite)
THROTTLE_SECS = 0.1

# ----------------------------
# Utilities
# ----------------------------

def to_int(x, default=0):
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        return default

def safe_ratio(num, den):
    den = den if den else 0
    return (num / den) if den else 0.0

def backoff_sleep(k):
    # exponential backoff with jitter
    sleep = BASE_SLEEP * (2 ** k) + random.uniform(0, 0.25)
    time.sleep(sleep)

def yt_call_with_retries(fn, *args, **kwargs):
    """Wrap any api.execute() with retries for transient errors."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = fn(*args, **kwargs).execute()
            time.sleep(THROTTLE_SECS)
            return resp
        except HttpError as e:
            status = getattr(e, "resp", None).status if hasattr(e, "resp") else None
            # Retry on 5xx, rate/quota errors; otherwise re-raise
            should_retry = False
            if status and 500 <= int(status) < 600:
                should_retry = True
            else:
                # Check error reasons
                try:
                    details = e.error_details if hasattr(e, "error_details") else None
                except Exception:
                    details = None
                body = getattr(e, "content", b"")
                text = body.decode("utf-8", errors="ignore")
                retry_markers = [
                    "quotaExceeded",
                    "userRateLimitExceeded",
                    "rateLimitExceeded",
                    "backendError",
                    "internalError",
                    "serviceUnavailable",
                    "operationAborted",
                    "playlistItemThrottleExceeded"
                ]
                if any(m in text for m in retry_markers):
                    should_retry = True

            if should_retry and attempt < MAX_RETRIES - 1:
                backoff_sleep(attempt)
                continue
            # Last attempt or non-retryable
            # Don’t crash — bubble up to caller to handle gracefully
            raise
        except Exception:
            if attempt < MAX_RETRIES - 1:
                backoff_sleep(attempt)
                continue
            raise

# ----------------------------
# Core class
# ----------------------------

class YTInfluencerFinder:
    def __init__(self, api_key: str):
        self.youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=api_key)

    # 1) Keyword search for channels
    def search_channels(self, keywords: str, max_pages: int = 2,
                        region: Optional[str] = None,
                        relevance_language: Optional[str] = None) -> List[str]:
        channel_ids = []
        page_token = None

        for _ in range(max_pages):
            resp = yt_call_with_retries(
                self.youtube.search().list,
                part="snippet",
                q=keywords,
                type="channel",
                maxResults=50,
                regionCode=region,
                relevanceLanguage=relevance_language,
                pageToken=page_token
            )
            for item in resp.get("items", []):
                # In search results, channelId is under snippet
                cid = item["snippet"].get("channelId")
                if cid:
                    channel_ids.append(cid)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        # de-dupe, preserve order
        seen, out = set(), []
        for c in channel_ids:
            if c not in seen:
                out.append(c); seen.add(c)
        return out

    # 2) Fetch channel stats (snippet, statistics, contentDetails)
    def get_channel_rows(self, channel_ids: List[str]) -> List[Dict[str, Any]]:
        rows = []
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i:i+50]
            try:
                resp = yt_call_with_retries(
                    self.youtube.channels().list,
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch),
                    maxResults=50
                )
            except HttpError:
                # If channels batch fails (rare), skip it but keep going
                continue

            for it in resp.get("items", []):
                s = it.get("statistics", {}) or {}
                uploads = (it.get("contentDetails", {})
                             .get("relatedPlaylists", {})
                             .get("uploads"))
                rows.append({
                    "channel_id": it.get("id"),
                    "title": (it.get("snippet", {}) or {}).get("title", ""),
                    "description": (it.get("snippet", {}) or {}).get("description", ""),
                    "subs": to_int(s.get("subscriberCount"), default=None)
                        if not s.get("hiddenSubscriberCount") else None,
                    "video_count": to_int(s.get("videoCount")),
                    "view_count": to_int(s.get("viewCount")),
                    "uploads_playlist": uploads
                })
        return rows

    # 3a) Preferred: get recent videos from uploads playlist
    def get_recent_videos_from_uploads(self, uploads_playlist_id: str, cap: int = 10) -> List[str]:
        video_ids, page_token = [], None
        while len(video_ids) < cap:
            try:
                resp = yt_call_with_retries(
                    self.youtube.playlistItems().list,
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, cap - len(video_ids)),
                    pageToken=page_token
                )
            except HttpError:
                # If playlist doesn’t exist or private → return what we have
                break
            for it in resp.get("items", []):
                vid = (it.get("contentDetails") or {}).get("videoId")
                if vid:
                    video_ids.append(vid)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return video_ids

    # 3b) Fallback: search the channel’s recent videos via search.list
    def get_recent_videos_by_channel_search(self, channel_id: str, cap: int = 10) -> List[str]:
        video_ids = []
        page_token = None
        while len(video_ids) < cap:
            try:
                resp = yt_call_with_retries(
                    self.youtube.search().list,
                    part="id",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    maxResults=min(50, cap - len(video_ids)),
                    pageToken=page_token
                )
            except HttpError:
                break
            for it in resp.get("items", []):
                vid = (it.get("id") or {}).get("videoId")
                if vid:
                    video_ids.append(vid)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return video_ids

    # 4) Fetch per-video stats
    def get_video_stats(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        out = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            try:
                resp = yt_call_with_retries(
                    self.youtube.videos().list,
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch)
                )
            except HttpError:
                continue
            for v in resp.get("items", []):
                st = v.get("statistics", {}) or {}
                out.append({
                    "video_id": v.get("id"),
                    "title": (v.get("snippet", {}) or {}).get("title", ""),
                    "views": to_int(st.get("viewCount")),
                    "likes": to_int(st.get("likeCount")),
                    "comments": to_int(st.get("commentCount")),
                })
        return out

    # 5) Scoring / aggregation
    def score_channel(self, row: Dict[str, Any], videos: List[Dict[str, Any]]) -> float:
        subs = row.get("subs") or 0
        total_views = sum(v["views"] for v in videos) if videos else 0
        avg_views = total_views / max(1, len(videos))
        eng = safe_ratio(sum(v["likes"] + v["comments"] for v in videos), total_views)

        # Simple, tunable heuristic
        return (
            0.5 * (subs / 1_000) +
            0.4 * (avg_views / 1_000) +
            0.1 * (eng * 100)
        )

    # 6) Orchestration (with fallbacks)
    def find_influencers(self, keywords: str, region: Optional[str] = None,
                         relevance_language: Optional[str] = None,
                         pages: int = 2, per_channel_video_cap: int = 10) -> List[Dict[str, Any]]:
        channel_ids = self.search_channels(
            keywords, max_pages=pages, region=region, relevance_language=relevance_language
        )
        if not channel_ids:
            return []

        rows = self.get_channel_rows(channel_ids)
        results = []
        for r in rows:
            uploads = r.get("uploads_playlist")
            vids = []
            if uploads:
                vids = self.get_recent_videos_from_uploads(uploads, cap=per_channel_video_cap)

            # Fallback if uploads playlist missing/invalid/empty
            if not vids:
                cid = r.get("channel_id")
                if cid:
                    vids = self.get_recent_videos_by_channel_search(cid, cap=per_channel_video_cap)

            # Last line of defense: if still nothing, keep channel but with zeros
            vstats = self.get_video_stats(vids) if vids else []
            avg_recent_views = round(sum(v["views"] for v in vstats) / max(1, len(vstats)), 2) if vstats else 0.0
            engagement_rate = round(
                safe_ratio(sum(v["likes"] + v["comments"] for v in vstats),
                           sum(v["views"] for v in vstats)), 4
            ) if vstats else 0.0

            score = round(self.score_channel(r, vstats), 3)
            enriched = {
                **r,
                "avg_recent_views": avg_recent_views,
                "engagement_rate": engagement_rate,
                "score": score
            }
            results.append(enriched)

        # Sort best-first
        results.sort(key=lambda x: (x["score"], x.get("subs") or 0, x.get("avg_recent_views") or 0), reverse=True)
        return results

# ----------------------------
# CLI-style runner
# ----------------------------

def export_csv(rows: List[Dict[str, Any]], path="influencers.csv"):
    if not rows:
        # ensure file exists with header if nothing found
        base_fields = [
            "channel_id", "title", "description",
            "subs", "video_count", "view_count",
            "uploads_playlist", "avg_recent_views",
            "engagement_rate", "score"
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=base_fields).writeheader()
        return

    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def search(keywords="wireless earbuds review"):
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY") or ""
    if not api_key:
        raise SystemExit("Missing YOUTUBE_API_KEY (put it in a .env file or export it)")
    t0 = time.time()
    finder = YTInfluencerFinder(api_key)

    # Customize your query & region/language
    # keywords set in params
    region = "CA"               # bias to Canada; set to None to disable
    relevance_language = "en"   # bias to English; set to None to disable

    try:
        results = finder.find_influencers(
            keywords=keywords,
            region=region,
            relevance_language=relevance_language,
            pages=2,
            per_channel_video_cap=10
        )
    except Exception as e:
        print("Error while searching:", e)
        results = []
    dt = time.time() - t0
    print(f"(processed in {dt:.2f}s)\n")

    export_csv(results, "influencers.csv")

    print("Top 5:")
    for r in results[:5]:
        print(
            r.get("title", "—"),
            r.get("subs"),
            r.get("avg_recent_views"),
            r.get("engagement_rate"),
            r.get("score")
        )

#f __name__ == "__main__":
    #search()