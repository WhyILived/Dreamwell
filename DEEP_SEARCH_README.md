# Deep Search System for Dreamwell

This document describes the deep search functionality that integrates YouTube video downloading with Twelve Labs AI analysis for comprehensive influencer content analysis.

## 🚀 Features

- **YouTube Video Download**: Automatically downloads YouTube videos using yt-dlp
- **Twelve Labs Integration**: Advanced AI analysis of video content, audio, and visual elements
- **Custom Analysis Prompts**: Tailored analysis for influencer marketing potential
- **Real-time Processing**: Live status updates during analysis
- **Results Caching**: Avoids re-analyzing the same videos
- **Comprehensive Results**: Summary, chapters, and custom analysis

## 📁 File Structure

```
├── deep_search_service.py      # Core deep search functionality
├── deep_search_routes.py       # Flask API endpoints
├── models.py                   # Database models (includes DeepSearchCache)
├── app.py                      # Main Flask app (updated with deep search routes)
├── requirements.txt            # Dependencies (updated)
├── test_deep_search.py         # Test script
└── my-app/
    ├── lib/api.ts             # Frontend API client (updated)
    └── app/dashboard/influencers/page.tsx  # UI with deep search button
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Twelve Labs API

Set your Twelve Labs API key as an environment variable:

```bash
# Windows PowerShell
$env:TWELVE_LABS_API_KEY="your-api-key-here"

# Windows Command Prompt
set TWELVE_LABS_API_KEY=your-api-key-here

# Linux/Mac
export TWELVE_LABS_API_KEY=your-api-key-here
```

Or create a `.env` file:
```
TWELVE_LABS_API_KEY=your-api-key-here
```

### 3. Install FFmpeg (Required for video processing)

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract and add to your system PATH

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### 4. Initialize Database

```bash
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database tables created successfully')"
```

### 5. Test the Installation

```bash
python test_deep_search.py
```

## 🎯 Usage

### Backend API Endpoints

#### Start Deep Search Analysis
```http
POST /api/auth/deep-search/analyze
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "channel_id": "CHANNEL_ID",
  "product_id": 123,
  "influencer_name": "Influencer Name",
  "custom_prompt": "Optional custom analysis prompt"
}
```

#### Get Analysis Status
```http
GET /api/auth/deep-search/status/{video_url}
Authorization: Bearer <jwt-token>
```

#### Get Analysis History
```http
GET /api/auth/deep-search/history
Authorization: Bearer <jwt-token>
```

#### Retry Failed Analysis
```http
POST /api/auth/deep-search/retry/{analysis_id}
Authorization: Bearer <jwt-token>
```

### Frontend Usage

1. Navigate to the Influencers page
2. Find an influencer with available video content
3. Click the "🔍 Deep Search" button next to the influencer
4. Wait for the analysis to complete (this may take a few minutes)
5. View the comprehensive analysis results in the modal

## 📊 Analysis Results

The deep search provides three types of analysis:

### 1. Video Summary
- AI-generated summary of the video content
- Key topics and themes
- Overall content quality assessment

### 2. Video Chapters
- Automatic chapter detection with timestamps
- Chapter titles and summaries
- Content structure analysis

### 3. Custom Influencer Analysis
- Brand fit assessment
- Content quality evaluation
- Collaboration potential analysis
- Audience insights
- Performance indicators

## 🔧 Configuration

### Twelve Labs Settings

The system uses the following Twelve Labs configuration:

```python
ENGINE = "pegasus1.2"           # AI model
LANGUAGE = "en"                 # Analysis language
INDEX_NAME = "dreamwell_index"  # Index name for video storage
```

### Custom Analysis Prompts

The system automatically generates custom prompts based on:
- Influencer name
- Product information
- Brand requirements

You can also provide custom prompts for specific analysis needs.

## 🗄️ Database Schema

### DeepSearchCache Table

```sql
CREATE TABLE deep_search_cache (
    id INTEGER PRIMARY KEY,
    video_url VARCHAR(1024) NOT NULL,
    video_id VARCHAR(32),
    channel_id VARCHAR(64),
    video_file_path VARCHAR(1024),
    twelve_labs_video_id VARCHAR(64),
    summary TEXT,
    chapters TEXT,  -- JSON string
    analysis TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🚨 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'twelvelabs'"**
   - Run: `pip install twelvelabs`

2. **"FFmpeg not found"**
   - Install FFmpeg and add to system PATH

3. **"TWELVE_LABS_API_KEY not found"**
   - Set the environment variable with your API key

4. **Video download fails**
   - Check internet connection
   - Verify YouTube URL is valid
   - Ensure video is not private or region-locked

5. **Analysis fails**
   - Check Twelve Labs API key validity
   - Verify API quota limits
   - Check video file size (large videos may timeout)

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Considerations

- API keys are stored as environment variables
- Video files are automatically cleaned up after analysis
- Database queries are parameterized to prevent SQL injection
- JWT authentication required for all endpoints

## 📈 Performance Notes

- Video download time depends on video length and quality
- Twelve Labs analysis typically takes 2-5 minutes per video
- Results are cached to avoid re-analysis
- Large videos (>1GB) may require more processing time

## 🎉 Success!

Your deep search system is now ready! The integration provides:

✅ YouTube video downloading  
✅ Twelve Labs AI analysis  
✅ Custom influencer marketing insights  
✅ Real-time processing status  
✅ Comprehensive results display  
✅ Database caching for efficiency  

Start the servers and begin analyzing influencer content with AI-powered insights!
