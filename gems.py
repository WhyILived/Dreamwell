#!/usr/bin/env python3
"""
Gems - API Integration Module
Centralized location for all external API calls and prompts
"""

import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Module-level flags to avoid noisy repeated init logs
_GEMINI_INIT_LOGGED = False
_YOUTUBE_INIT_LOGGED = False

class GemsAPI:
    """Centralized API integration class"""
    
    def __init__(self):
        """Initialize API clients and configurations"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        
        # Initialize API clients
        self._init_gemini()
        self._init_youtube()
    
    def _init_gemini(self):
        """Initialize Gemini API client"""
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                global _GEMINI_INIT_LOGGED
                if not _GEMINI_INIT_LOGGED:
                    print("✅ Gemini API initialized")
                    _GEMINI_INIT_LOGGED = True
            except ImportError:
                print("❌ google-generativeai not installed")
                self.gemini_model = None
        else:
            print("❌ GEMINI_API_KEY not found")
            self.gemini_model = None
    
    def _init_youtube(self):
        """Initialize YouTube API client"""
        if self.youtube_api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
                global _YOUTUBE_INIT_LOGGED
                if not _YOUTUBE_INIT_LOGGED:
                    print("✅ YouTube API initialized")
                    _YOUTUBE_INIT_LOGGED = True
            except ImportError:
                print("❌ google-api-python-client not installed")
                self.youtube = None
        else:
            print("❌ YOUTUBE_API_KEY not found")
            self.youtube = None

    # ==================== YOUTUBE API FUNCTIONS ====================
    
    def search_channels_with_filters(self, keywords: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for YouTube channels with advanced filters
        
        Args:
            keywords: Search keywords
            filters: Dictionary of search filters
            
        Returns:
            List[Dict]: Channel information with metadata
        """
        if not self.youtube:
            return []
        
        # Default filters
        default_filters = {
            'max_results': 50,
            'region_code': 'US',
            'relevance_language': 'en',
            'order': 'relevance',
            'channel_type': 'any',
            'video_duration': 'any',
            'video_definition': 'any',
            'video_caption': 'any',
            'video_license': 'any',
            'published_after': None,
            'published_before': None
        }
        
        # Merge with provided filters
        search_params = {**default_filters, **(filters or {})}
        
        try:
            # Build search parameters
            search_kwargs = {
                'part': 'snippet',
                'q': keywords,
                'type': 'channel',
                'maxResults': min(search_params['max_results'], 50),
                'order': search_params['order']
            }
            
            # Add optional filters
            if search_params['region_code']:
                search_kwargs['regionCode'] = search_params['region_code']
            if search_params['relevance_language']:
                search_kwargs['relevanceLanguage'] = search_params['relevance_language']
            if search_params['channel_type'] != 'any':
                search_kwargs['channelType'] = search_params['channel_type']
            if search_params['published_after']:
                search_kwargs['publishedAfter'] = search_params['published_after']
            if search_params['published_before']:
                search_kwargs['publishedBefore'] = search_params['published_before']
            
            # Execute search
            request = self.youtube.search().list(**search_kwargs)
            response = request.execute()
            
            channels = []
            for item in response.get('items', []):
                channel_info = {
                    'channel_id': item['snippet']['channelId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'published_at': item['snippet']['publishedAt'],
                    'search_keywords': keywords,
                    'filters_applied': search_params
                }
                channels.append(channel_info)
            
            return channels
            
        except Exception as e:
            print(f"Error searching channels: {e}")
            return []
    
    def search_videos_with_filters(self, keywords: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos with advanced filters
        
        Args:
            keywords: Search keywords
            filters: Dictionary of search filters
            
        Returns:
            List[Dict]: Video information with metadata
        """
        if not self.youtube:
            return []
        
        # Default filters
        default_filters = {
            'max_results': 50,
            'region_code': 'US',
            'relevance_language': 'en',
            'order': 'relevance',
            'video_duration': 'any',
            'video_definition': 'any',
            'video_caption': 'any',
            'video_license': 'any',
            'published_after': None,
            'published_before': None
        }
        
        # Merge with provided filters
        search_params = {**default_filters, **(filters or {})}
        
        try:
            # Build search parameters
            search_kwargs = {
                'part': 'snippet',
                'q': keywords,
                'type': 'video',
                'maxResults': min(search_params['max_results'], 50),
                'order': search_params['order']
            }
            
            # Add optional filters
            if search_params['region_code']:
                search_kwargs['regionCode'] = search_params['region_code']
            if search_params['relevance_language']:
                search_kwargs['relevanceLanguage'] = search_params['relevance_language']
            if search_params['video_duration'] != 'any':
                search_kwargs['videoDuration'] = search_params['video_duration']
            if search_params['video_definition'] != 'any':
                search_kwargs['videoDefinition'] = search_params['video_definition']
            if search_params['video_caption'] != 'any':
                search_kwargs['videoCaption'] = search_params['video_caption']
            if search_params['video_license'] != 'any':
                search_kwargs['videoLicense'] = search_params['video_license']
            if search_params['published_after']:
                search_kwargs['publishedAfter'] = search_params['published_after']
            if search_params['published_before']:
                search_kwargs['publishedBefore'] = search_params['published_before']
            
            # Execute search
            request = self.youtube.search().list(**search_kwargs)
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'search_keywords': keywords,
                    'filters_applied': search_params
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []

    # ==================== GEMINI API FUNCTIONS ====================
    
    def generate_keywords_from_website(self, url: str, top_n: int = 5) -> List[str]:
        """
        Generate keywords from website content using Gemini AI
        
        Args:
            url: Website URL to analyze
            top_n: Number of keywords to generate
            
        Returns:
            List[str]: Generated keywords
        """
        if not self.gemini_model:
            print("❌ Gemini API not available")
            return []
        
        try:
            # Import scraper functions for content extraction
            from scraper import normalize_url, fetch, extract_weighted_text
            
            print(f"🌐 Fetching website content: {url}")
            # Get website content
            url = normalize_url(url)
            html_content = fetch(url)
            
            # Extract text content for Gemini
            buckets = extract_weighted_text(html_content)
            
            # Combine all text content
            all_text = ""
            for tag_type, texts in buckets.items():
                for text in texts:
                    all_text += text + " "
            
            # Limit content length for API
            all_text = all_text[:8000]  # Reasonable limit for Gemini
            
            print(f"🤖 Sending content to Gemini for keyword analysis...")
            
            # Create prompt for Gemini
            prompt = f"""
            You are an AI assistant for an influencer marketing platform. Your job is to analyze a company's website and extract the most relevant keywords that would help find the right YouTube influencers for sponsorship opportunities.

            Website URL: {url}
            Website Content: {all_text}

            Based on this website content, extract {top_n} keywords that best describe:
            1. What the company does
            2. Their products/services
            3. Their target audience
            4. Their industry/niche
            5. Key themes and topics

            Requirements:
            - Keywords should be relevant for finding YouTube influencers
            - Include both single words and 2-word phrases
            - Focus on terms that influencers would use in their content
            - Avoid generic terms like "company", "business", "website"
            - Make keywords specific and actionable for influencer search

            Return ONLY a comma-separated list of keywords, no explanations or formatting.
            Example: "AI technology, machine learning, data science, tech innovation, software development"
            """
            
            # Get response from Gemini
            response = self.gemini_model.generate_content(prompt)
            keywords_text = response.text.strip()
            
            # Parse the response
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Limit to requested number
            keywords = keywords[:top_n]
            
            print(f"✅ Generated {len(keywords)} keywords using Gemini AI")
            for i, keyword in enumerate(keywords, 1):
                print(f"{i:2d}. {keyword}")
            
            return keywords
            
        except Exception as e:
            print(f"❌ Error with Gemini keyword generation: {e}")
            return []

    # ==================== CACHING FUNCTIONS ====================
    
    def _get_cache_key(self, keywords: str, search_type: str, filters: Dict[str, Any] = None) -> str:
        """Generate a cache key for the search"""
        filters_str = json.dumps(filters, sort_keys=True) if filters else "default"
        return f"{keywords}|{search_type}|{filters_str}"
    
    def _get_cached_results(self, keywords: str, search_type: str, filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results if available and not expired"""
        try:
            from models import db, YouTubeSearchCache
            
            norm_kw = (keywords or "").strip().lower()
            
            # Primary: most recent non-expired cache for same keyword/search_type (ignore filters)
            fallback = (YouTubeSearchCache
                        .query
                        .filter_by(keywords=norm_kw, search_type=search_type)
                        .order_by(YouTubeSearchCache.created_at.desc())
                        .first())
            if fallback and not fallback.is_expired():
                print(f"📦 Using cached results for '{norm_kw}' ({search_type})")
                return json.loads(fallback.results_data)
            elif fallback:
                # Remove expired fallback entry
                db.session.delete(fallback)
                db.session.commit()
                print(f"🗑️  Removed expired cache entry for '{norm_kw}'")
            
            # Optional: exact match path (kept for future use, but not required)
            filters_json = json.dumps(filters, sort_keys=True) if filters else None
            cache_entry = YouTubeSearchCache.query.filter_by(
                keywords=norm_kw,
                search_type=search_type,
                filters_applied=filters_json
            ).first()
            if cache_entry and not cache_entry.is_expired():
                print(f"📦 Using cached results for '{norm_kw}' ({search_type}) [exact]")
                return json.loads(cache_entry.results_data)
            elif cache_entry:
                db.session.delete(cache_entry)
                db.session.commit()
                print(f"🗑️  Removed expired cache entry for '{norm_kw}' [exact]")
            
            return None
            
        except Exception as e:
            print(f"Error accessing cache: {e}")
            return None
    
    def _save_to_cache(self, keywords: str, search_type: str, results: List[Dict[str, Any]], filters: Dict[str, Any] = None, cache_duration_hours: int = 24):
        """Save search results to cache. For video searches, store only video IDs."""
        try:
            from models import db, YouTubeSearchCache
            
            filters_json = json.dumps(filters, sort_keys=True) if filters else None
            # If this is a video search, store only list of video IDs to reduce payload
            if search_type == 'videos':
                video_ids = [r.get('video_id') for r in results if r.get('video_id')]
                results_json = json.dumps(video_ids)
            else:
                results_json = json.dumps(results)
            
            norm_kw = (keywords or "").strip().lower()
            # Remove any existing cache entries for this search
            existing_entries = YouTubeSearchCache.query.filter_by(
                keywords=norm_kw,
                search_type=search_type,
                filters_applied=filters_json
            ).all()
            
            for entry in existing_entries:
                db.session.delete(entry)
            
            # Create new cache entry
            cache_entry = YouTubeSearchCache(
                keywords=norm_kw,
                search_type=search_type,
                results_data=results_json,
                filters_applied=filters_json,
                cache_duration_hours=cache_duration_hours
            )
            
            db.session.add(cache_entry)
            db.session.commit()
            
            print(f"💾 Cached {len(results)} results for '{keywords}' ({search_type}) - expires in {cache_duration_hours}h")
            
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def search_channels_with_cache(self, keywords: str, filters: Dict[str, Any] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Search for channels with caching support"""
        # Check cache first
        if use_cache:
            cached_results = self._get_cached_results(keywords, 'channels', filters)
            if cached_results is not None:
                return cached_results
        
        # Perform actual search
        results = self.search_channels_with_filters(keywords, filters)
        
        # Save to cache
        if results and use_cache:
            self._save_to_cache(keywords, 'channels', results, filters)
        
        return results
    
    def search_videos_with_cache(self, keywords: str, filters: Dict[str, Any] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Search for videos with caching support"""
        # Check cache first
        if use_cache:
            cached_results = self._get_cached_results(keywords, 'videos', filters)
            if cached_results is not None:
                return cached_results
        
        # Perform actual search
        results = self.search_videos_with_filters(keywords, filters)

        # Persist per-video details into VideoCache (and enrich with stats/transcripts);
        # also compute/channel CPM estimates into ChannelCache.
        try:
            from models import db, VideoCache, ChannelCache
            from cpm import estimate_for_channel
            # Collect IDs for batched stats calls
            channel_ids = list({r.get('channel_id') for r in results if r.get('channel_id')})
            video_ids = [r.get('video_id') for r in results if r.get('video_id')]
            ch_stats = self.get_channels_stats(channel_ids)
            v_stats = self.get_videos_stats(video_ids)
            # build or update entries
            for r in results:
                vid = r.get('video_id')
                if not vid:
                    continue
                vc = VideoCache.query.filter_by(video_id=vid).first()
                if not vc:
                    vc = VideoCache(video_id=vid)
                    db.session.add(vc)
                vc.title = r.get('title')
                vc.description = r.get('description')
                vc.channel_id = r.get('channel_id')
                vc.channel_title = r.get('channel_title')
                vc.published_at = r.get('published_at')
                vc.thumbnail = r.get('thumbnail')
                # Channel-level enrichments
                cstat = ch_stats.get(r.get('channel_id') or "", {})
                vc.country = cstat.get('country')
                vc.subscriber_count = cstat.get('subscriber_count')
                # Video-level stats
                vstat = v_stats.get(vid, {})
                vc.view_count = vstat.get('views')
                # Transcript (best-effort, may be None)
                try:
                    vc.transcript = self.get_video_transcript(vid) or vc.transcript
                except Exception:
                    pass
                # Average views per video using channel totals: total_channel_views / total_videos
                try:
                    total_views = cstat.get('view_count') or 0
                    total_videos = cstat.get('video_count') or 0
                    vc.avg_recent_views = int(total_views / max(1, total_videos)) if (total_views or total_videos) else None
                except Exception:
                    pass

            # Compute/update per-channel CPM estimates
            for cid in channel_ids:
                # derive signals from latest cached videos
                rows = VideoCache.query.filter_by(channel_id=cid).order_by(VideoCache.updated_at.desc()).limit(10).all()
                if not rows:
                    continue
                country = rows[0].country
                language = 'en'  # best-effort default; could be inferred later
                subscribers = rows[0].subscriber_count
                # avg_recent_views: total_channel_views / total_videos from channel statistics
                cstat2 = ch_stats.get(cid, {})
                try:
                    total_views2 = cstat2.get('view_count') or 0
                    total_videos2 = cstat2.get('video_count') or 0
                    avg_recent_views = int(total_views2 / max(1, total_videos2)) if (total_views2 or total_videos2) else None
                except Exception:
                    avg_recent_views = None
                # engagement_rate: compute from likes+comments over views for recent videos
                try:
                    vids2 = [r.video_id for r in rows]
                    vstats2 = self.get_videos_stats(vids2)
                    total_views = 0
                    total_interactions = 0
                    for vid, st in vstats2.items():
                        vcount = st.get('views') or 0
                        lcount = st.get('likes') or 0
                        ccount = st.get('comments') or 0
                        total_views += vcount
                        total_interactions += (lcount + ccount)
                    engagement_rate = (total_interactions / total_views) if total_views else None
                except Exception:
                    engagement_rate = None
                # niche: infer from channel title rudimentarily or set default
                title_lc = (rows[0].channel_title or '').lower()
                niche = 'fitness' if 'fitness' in title_lc else 'tech' if 'tech' in title_lc else 'default'

                est = estimate_for_channel(
                    niche=niche,
                    country=country,
                    language=language,
                    avg_recent_views=avg_recent_views,
                    engagement_rate=engagement_rate,
                    subscribers=subscribers,
                )
                ch = ChannelCache.query.filter_by(channel_id=cid).first()
                if not ch:
                    ch = ChannelCache(channel_id=cid)
                    db.session.add(ch)
                ch.title = rows[0].channel_title
                ch.country = country
                ch.language = language
                ch.niche = niche
                ch.subscribers = subscribers
                ch.avg_recent_views = avg_recent_views
                ch.engagement_rate = engagement_rate
                ch.cpm_min_usd, ch.cpm_max_usd = est["cpm_usd"]
                ch.rpm_min_usd, ch.rpm_max_usd = est["rpm_usd"]
            db.session.commit()
        except Exception as e:
            print(f"Error upserting VideoCache: {e}")
        
        # Save to cache
        if results and use_cache:
            self._save_to_cache(keywords, 'videos', results, filters)
        
        # Return only video IDs to align with cache format
        return [r.get('video_id') for r in results if r.get('video_id')]

    # ==================== ENRICHMENT HELPERS ====================
    def get_channels_stats(self, channel_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch channel snippet/statistics for a list of channel IDs"""
        if not self.youtube or not channel_ids:
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        try:
            for i in range(0, len(channel_ids), 50):
                batch = channel_ids[i:i+50]
                req = self.youtube.channels().list(part="snippet,statistics", id=",".join(batch), maxResults=50)
                resp = req.execute()
                for item in resp.get("items", []):
                    cid = item.get("id")
                    sn = item.get("snippet", {}) or {}
                    st = item.get("statistics", {}) or {}
                    out[cid] = {
                        "subscriber_count": int(st.get("subscriberCount", 0)) if not st.get("hiddenSubscriberCount") else None,
                        "view_count": int(st.get("viewCount", 0)) if st.get("viewCount") else 0,
                        "video_count": int(st.get("videoCount", 0)) if st.get("videoCount") else 0,
                        "country": sn.get("country")
                    }
        except Exception as e:
            print(f"Error fetching channel stats: {e}")
        return out

    def get_videos_stats(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch per-video statistics (views) for a list of video IDs"""
        if not self.youtube or not video_ids:
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        try:
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                req = self.youtube.videos().list(part="statistics", id=",".join(batch), maxResults=50)
                resp = req.execute()
                for item in resp.get("items", []):
                    vid = item.get("id")
                    st = item.get("statistics", {}) or {}
                    out[vid] = {
                        "views": int(st.get("viewCount", 0)) if st.get("viewCount") else 0,
                        "likes": int(st.get("likeCount", 0)) if st.get("likeCount") else 0,
                        "comments": int(st.get("commentCount", 0)) if st.get("commentCount") else 0,
                    }
        except Exception as e:
            print(f"Error fetching video stats: {e}")
        return out

    # ==================== TRANSCRIPTS (NO OAUTH) ====================
    def get_video_transcript(self, video_id: str, languages: Optional[List[str]] = None) -> Optional[str]:
        """Retrieve transcript text using youtube-transcript-api (no OAuth).

        Returns a single concatenated string or None if unavailable.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            langs = languages or ["en", "en-US", "en-GB"]
            ytt = YouTubeTranscriptApi()
            fetched = ytt.fetch(video_id, languages=langs)
            # fetched is iterable of snippets with .text, or use .to_raw_data()
            try:
                text = " ".join(getattr(seg, "text", "") for seg in fetched).strip()
                if text:
                    return text
            except Exception:
                pass
            raw = getattr(fetched, "to_raw_data", lambda: [])()
            return " ".join(seg.get("text", "") for seg in raw).strip() or None
        except Exception:
            return None

    # ==================== PRODUCT EXTRACTION ====================
    def extract_product_from_url(self, url: str) -> Dict[str, Any]:
        """Scrape page and use Gemini to extract name, category, and keywords (no price)."""
        out = {"name": None, "category": None, "keywords": []}
        try:
            # Fetch and truncate html
            html = fetch(url)  # reuse scraper's fetch if imported, else fallback
        except Exception:
            try:
                import requests
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                html = r.text[:150000]
            except Exception:
                html = ""
        if not self.gemini_model:
            return out
        prompt = f"""
        You are extracting product details from a webpage for influencer targeting.
        URL: {url}
        Page HTML (truncated):
        ```
        {html}
        ```

        Extract:
        - name: concise product name
        - category: short category tag (e.g., "fitness apparel", "tech gadget")
        - keywords: 2-3 concise search keywords relevant for finding videos from YouTube influencers who would be a good fit. Do not include the product name in the keywords.

        Respond in JSON with keys: name, category, keywords (array of strings).
        """
        try:
            resp = self.gemini_model.generate_content(prompt)
            import json as _json
            txt = (resp.text or "").strip()
            # Try to parse JSON
            start = txt.find("{")
            end = txt.rfind("}")
            if start != -1 and end != -1 and end > start:
                parsed = _json.loads(txt[start:end+1])
                # normalize
                out["name"] = parsed.get("name")
                out["category"] = parsed.get("category")
                kws = parsed.get("keywords") or []
                out["keywords"] = [str(k).strip() for k in kws if str(k).strip()]
        except Exception:
            pass
        return out
    
    def clear_expired_cache(self):
        """Remove all expired cache entries"""
        try:
            from models import db, YouTubeSearchCache
            
            expired_entries = YouTubeSearchCache.query.filter(
                YouTubeSearchCache.expires_at < db.func.now()
            ).all()
            
            count = len(expired_entries)
            for entry in expired_entries:
                db.session.delete(entry)
            
            db.session.commit()
            print(f"🗑️  Removed {count} expired cache entries")
            return count
            
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
            return 0
    
    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            from models import db, YouTubeSearchCache
            
            total_entries = YouTubeSearchCache.query.count()
            expired_entries = YouTubeSearchCache.query.filter(
                YouTubeSearchCache.expires_at < db.func.now()
            ).count()
            active_entries = total_entries - expired_entries
            
            return {
                'total_entries': total_entries,
                'active_entries': active_entries,
                'expired_entries': expired_entries
            }
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'total_entries': 0, 'active_entries': 0, 'expired_entries': 0}

# ==================== CONVENIENCE FUNCTIONS ====================

def generate_keywords(url: str, top_n: int = 5) -> List[str]:
    """Convenience function to generate keywords from website"""
    gems = GemsAPI()
    return gems.generate_keywords_from_website(url, top_n)

def search_channels(keywords: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Convenience function to search channels with filters"""
    gems = GemsAPI()
    return gems.search_channels_with_filters(keywords, filters)

def search_videos(keywords: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Convenience function to search videos with filters"""
    gems = GemsAPI()
    return gems.search_videos_with_filters(keywords, filters)

def get_pricing_estimate(influencer_data: Dict[str, Any]) -> str:
    """Convenience function to get pricing estimate"""
    gems = GemsAPI()
    return gems.get_influencer_pricing(influencer_data)

def search_recent_popular_videos(keywords: str, max_results: int = 50, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Search for videos uploaded within the last year, sorted by view count
    
    Args:
        keywords: Search keywords
        max_results: Maximum number of results (1-50)
        use_cache: Whether to use cached results if available
        
    Returns:
        List[Dict]: Video information with metadata
    """
    from datetime import datetime, timedelta
    
    # Calculate date one year ago
    one_year_ago = datetime.now() - timedelta(days=365)
    # Normalize to date-only (midnight) so repeat searches within a day
    # use the same filter string and hit the cache
    published_after = one_year_ago.strftime('%Y-%m-%dT00:00:00Z')
    
    filters = {
        'published_after': published_after,
        'order': 'viewCount',
        'max_results': max_results,
        'region_code': 'US',
        'relevance_language': 'en'
    }
    
    gems = GemsAPI()
    return gems.search_videos_with_cache(keywords, filters, use_cache)

def search_recent_popular_channels(keywords: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Search for channels with recent popular content (last year, sorted by view count)
    
    Args:
        keywords: Search keywords
        max_results: Maximum number of results (1-50)
        
    Returns:
        List[Dict]: Channel information with metadata
    """
    from datetime import datetime, timedelta
    
    # Calculate date one year ago
    one_year_ago = datetime.now() - timedelta(days=365)
    published_after = one_year_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    filters = {
        'published_after': published_after,
        'order': 'viewCount',
        'max_results': max_results,
        'region_code': 'US',
        'relevance_language': 'en'
    }
    
    gems = GemsAPI()
    return gems.search_channels_with_filters(keywords, filters)

# ==================== TESTING ====================

if __name__ == "__main__":
    # Test the API initialization
    gems = GemsAPI()
    print("\n🧪 Gems API initialized successfully!")
    
    # Test keyword generation
    test_url = "https://www.dreamwell.ai"
    keywords = gems.generate_keywords_from_website(test_url, 5)
    print(f"Generated keywords: {keywords}")
