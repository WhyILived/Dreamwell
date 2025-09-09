#!/usr/bin/env python3
"""
Quick script to fetch and print a video's transcript (no OAuth).

Usage:
  python transcript_test.py <VIDEO_ID> [lang]

Examples:
  python transcript_test.py dQw4w9WgXcQ
  python transcript_test.py dQw4w9WgXcQ en
"""

import sys
from typing import List

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python transcript_test.py <VIDEO_ID> [lang]")
        return 1

    video_id = sys.argv[1].strip()
    langs: List[str] = [sys.argv[2]] if len(sys.argv) > 2 else ["en", "en-US", "en-GB"]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("youtube-transcript-api is not installed. Run: pip install youtube-transcript-api")
        return 2

    try:
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id, languages=langs)
        # Try iterating fetched (snippets API), fallback to raw data
        try:
            text = " ".join(getattr(seg, "text", "") for seg in fetched).strip()
        except Exception:
            text = ""
        if not text and hasattr(fetched, "to_raw_data"):
            raw = fetched.to_raw_data()
            text = " ".join(seg.get("text", "") for seg in raw).strip()
        if text:
            print("\n=== Transcript ===\n")
            print(text)
            return 0
        print("No transcript available.")
        return 3
    except Exception as e:
        print(f"No transcript available or error: {e}")
        return 3

if __name__ == "__main__":
    raise SystemExit(main())


