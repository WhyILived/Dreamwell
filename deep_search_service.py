import os
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from twelvelabs import TwelveLabs
import yt_dlp
from models import db, DeepSearchCache
from config import config

# ======= Twelve Labs Config =======
API_KEY = os.environ.get('TL_API_KEY', '') or os.environ.get('TWELVE_LABS_API_KEY', '')
ENGINE = "pegasus1.2"
LANGUAGE = "en"
INDEX_NAME = "dreamwell_index"
# ==================================

client = TwelveLabs(api_key=API_KEY) if API_KEY else None

def extract_video_id_from_url(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/v/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def is_valid_video_url(url: str) -> bool:
    """Check if URL is a valid single video URL (not channel or playlist)."""
    # Check if it's a channel URL
    if '/channel/' in url or '/c/' in url or '/user/' in url or '/@' in url:
        return False
    
    # Check if it's a playlist URL
    if '/playlist' in url:
        return False
    
    # Check if it has a video ID
    video_id = extract_video_id_from_url(url)
    return video_id is not None

def download_video(url: str, output_dir: str = "downloads") -> str:
    """
    Downloads the YouTube video and returns the actual full path to the saved file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegMetadata'}],
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def get_or_create_index(index_name: str):
    """
    Retrieves the TwelveLabs index by name, or creates it if it doesn't exist.
    """
    if not client:
        raise RuntimeError("Twelve Labs API key not configured")
    
    # Convert pager to list
    indexes = list(client.indexes.list())
    for index in indexes:
        if index.index_name == index_name:
            return index

    # Create new index
    create_response = client.indexes.create(
        index_name=index_name,
        models=[{
            "model_name": ENGINE,
            "model_options": ["visual", "audio"]
        }]
    )
    
    # Get the created index by ID
    return client.indexes.retrieve(create_response.id)

def get_existing_video_id(index_id: str, filename: str) -> Optional[str]:
    """
    Checks if the given video file is already indexed and returns its video ID.
    """
    if not client:
        return None
        
    # Convert pager to list
    tasks = list(client.tasks.list(index_id=index_id))
    base_filename = os.path.basename(filename)

    matching_tasks = [
        task for task in tasks
        if task.status == "ready" and task.system_metadata
        and hasattr(task.system_metadata, 'filename')
        and os.path.basename(task.system_metadata.filename) == base_filename
    ]

    if matching_tasks:
        matching_tasks.sort(
            key=lambda t: datetime.fromisoformat(t.created_at.rstrip("Z"))
        )
        latest_task = matching_tasks[-1]
        return latest_task.video_id

    return None

def analyze_video_with_twelve_labs(file_path: str, custom_prompt: str = None) -> Dict[str, Any]:
    """
    Uploads a video to TwelveLabs if not already indexed,
    and returns summary, chapters, and custom analysis.
    """
    if not client:
        raise RuntimeError("Twelve Labs API key not configured")
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    index = get_or_create_index(INDEX_NAME)
    video_id = get_existing_video_id(index.id, file_path)

    if not video_id:
        print("📤 Uploading and indexing video...")
        # Use file object instead of file path for better compatibility
        with open(file_path, 'rb') as f:
            task = client.tasks.create(index_id=index.id, video_file=f)
        
        # Poll for completion since wait_for_done() doesn't exist in new API
        import time
        task_id = task.id
        print(f"Task created with ID: {task_id}")
        
        while True:
            task_status = client.tasks.retrieve(task_id)
            print(f"Task status: {task_status.status}")
            
            if task_status.status == "ready":
                video_id = task_status.video_id
                print(f"✅ Video indexed successfully: video_id={video_id}")
                break
            elif task_status.status == "failed":
                raise RuntimeError(f"Indexing failed (status: {task_status.status})")
            
            time.sleep(5)  # Wait 5 seconds before checking again
    else:
        print(f"✅ Using previously indexed video: video_id={video_id}")

    results = {
        'twelve_labs_video_id': video_id,
        'summary': '',
        'chapters': [],
        'analysis': ''
    }

    # Generate Summary
    print("📄 Generating summary...")
    res_summary = client.summarize(video_id=video_id, type="summary")
    results['summary'] = res_summary.summary

    # Generate Chapters
    print("📑 Generating chapters...")
    res_chapters = client.summarize(video_id=video_id, type="chapter")
    
    chapters = []
    for chapter in res_chapters.chapters:
        chapters.append({
            'chapter_number': chapter.chapter_number,
            'start': chapter.start,
            'end': chapter.end,
            'title': chapter.chapter_title,
            'summary': chapter.chapter_summary
        })
    results['chapters'] = chapters

    # Generate Custom Analysis if prompt provided
    if custom_prompt:
        print("🔍 Generating custom analysis...")
        res_analysis = client.analyze(video_id=video_id, prompt=custom_prompt)
        results['analysis'] = res_analysis.data

    return results

def create_influencer_analysis_prompt(influencer_name: str, product_name: str = None) -> str:
    """
    Creates a custom analysis prompt for influencer content analysis.
    """
    base_prompt = f"""Analyze this video content from {influencer_name} for influencer marketing potential. Focus on:

1. Content Quality & Engagement:
   - Video production quality (lighting, audio, editing)
   - Engagement indicators (viewer retention, comments, likes)
   - Content authenticity and relatability

2. Brand Fit Analysis:
   - How well the content style would fit with various brand types
   - Audience demographics and interests
   - Content themes and values alignment

3. Collaboration Potential:
   - Natural integration points for product placements
   - Sponsored content opportunities
   - Audience trust and credibility indicators

4. Content Performance Indicators:
   - Visual appeal and professional presentation
   - Storytelling ability and narrative structure
   - Call-to-action effectiveness

5. Audience Insights:
   - Target demographic characteristics
   - Engagement patterns and preferences
   - Community interaction quality

Provide specific timestamps and examples where relevant. Rate the overall influencer potential on a scale of 1-10 and explain your reasoning."""

    if product_name:
        base_prompt += f"\n\nSpecifically consider how this content would work for promoting: {product_name}"

    return base_prompt

def perform_deep_search(video_url: str, channel_id: str = None, custom_prompt: str = None, company_values: List[str] = None, company_country: str = "US", is_luxury: bool = False) -> Dict[str, Any]:
    """
    Performs a complete deep search: downloads video, analyzes with Twelve Labs.
    Returns comprehensive analysis results.
    """
    try:
        # Validate that this is a single video URL, not a channel or playlist
        if not is_valid_video_url(video_url):
            raise ValueError(f"Invalid video URL: {video_url}. Must be a specific YouTube video URL, not a channel or playlist.")
        
        # Check if we already have results for this video
        existing = DeepSearchCache.query.filter_by(video_url=video_url).first()
        if existing and existing.status == 'completed':
            return existing.to_dict()

        # Create or update cache entry
        cache_entry = existing or DeepSearchCache(video_url=video_url, channel_id=channel_id)
        cache_entry.status = 'processing'
        cache_entry.updated_at = datetime.utcnow()
        
        if not existing:
            db.session.add(cache_entry)
        db.session.commit()

        # Extract video ID
        video_id = extract_video_id_from_url(video_url)
        cache_entry.video_id = video_id

        # Download video
        print(f"📥 Downloading video: {video_url}")
        video_file_path = download_video(video_url)
        cache_entry.video_file_path = video_file_path
        db.session.commit()

        # Analyze with Twelve Labs
        print("🧠 Analyzing video with Twelve Labs...")
        analysis_results = analyze_video_with_twelve_labs(video_file_path, custom_prompt)
        
        # Update cache with Twelve Labs results
        cache_entry.twelve_labs_video_id = analysis_results['twelve_labs_video_id']
        cache_entry.summary = analysis_results['summary']
        cache_entry.chapters = json.dumps(analysis_results['chapters'])
        cache_entry.analysis = analysis_results['analysis']
        
        # Perform comprehensive analysis with Gemini
        if company_values:
            print("🤖 Performing comprehensive analysis with Gemini...")
            try:
                from gems import GemsAPI
                gems_api = GemsAPI()
                
                # Prepare deep search data for Gemini
                deep_search_data = {
                    'summary': analysis_results['summary'],
                    'chapters': analysis_results['chapters'],
                    'analysis': analysis_results['analysis']
                }
                
                # Get comprehensive analysis from Gemini
                gemini_analysis = gems_api.analyze_deep_search_with_gemini(
                    deep_search_data=deep_search_data,
                    company_values=company_values,
                    company_country=company_country,
                    is_luxury=is_luxury
                )
                
                if 'error' not in gemini_analysis:
                    # Store comprehensive scores
                    cache_entry.content_quality_score = gemini_analysis.get('content_quality_score')
                    cache_entry.values_alignment_score = gemini_analysis.get('values_alignment_score')
                    cache_entry.engagement_potential_score = gemini_analysis.get('engagement_potential_score')
                    cache_entry.brand_safety_score = gemini_analysis.get('brand_safety_score')
                    cache_entry.cultural_fit_score = gemini_analysis.get('cultural_fit_score')
                    cache_entry.influence_potential_score = gemini_analysis.get('influence_potential_score')
                    cache_entry.content_consistency_score = gemini_analysis.get('content_consistency_score')
                    cache_entry.audience_quality_score = gemini_analysis.get('audience_quality_score')
                    cache_entry.overall_score = gemini_analysis.get('overall_score')
                    
                    # Store analysis details
                    cache_entry.analysis_reasoning = json.dumps(gemini_analysis.get('reasoning', {}))
                    cache_entry.recommendations = json.dumps(gemini_analysis.get('recommendations', []))
                    cache_entry.risk_factors = json.dumps(gemini_analysis.get('risk_factors', []))
                    cache_entry.strengths = json.dumps(gemini_analysis.get('strengths', []))
                    cache_entry.analysis_timestamp = datetime.utcnow()
                    
                    print(f"✅ Comprehensive analysis completed - Overall Score: {gemini_analysis.get('overall_score', 'N/A')}")
                else:
                    print(f"⚠️  Gemini analysis failed: {gemini_analysis['error']}")
                    
            except Exception as e:
                print(f"⚠️  Error in Gemini analysis: {e}")
        
        cache_entry.status = 'completed'
        cache_entry.updated_at = datetime.utcnow()
        
        db.session.commit()

        # Keep video file for now to avoid cleanup issues
        # TODO: Add cleanup after successful processing
        print(f"📁 Video file kept at: {video_file_path}")

        return cache_entry.to_dict()

    except Exception as e:
        print(f"❌ Deep search failed: {str(e)}")
        
        # Update cache with error
        if 'cache_entry' in locals():
            cache_entry.status = 'failed'
            cache_entry.error_message = str(e)
            cache_entry.updated_at = datetime.utcnow()
            db.session.commit()
        
        raise e

def get_deep_search_status(video_url: str) -> Optional[Dict[str, Any]]:
    """
    Get the current status of a deep search operation.
    """
    cache_entry = DeepSearchCache.query.filter_by(video_url=video_url).first()
    return cache_entry.to_dict() if cache_entry else None
