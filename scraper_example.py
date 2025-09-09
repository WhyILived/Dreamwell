#!/usr/bin/env python3
"""
Example usage of the YouTube scraper
"""

from main import YouTubeScraper, export_to_csv, ChannelData
from datetime import datetime

def example_usage():
    """Example of how to use the YouTube scraper"""
    
    # Initialize scraper (will use mock data if no API key)
    scraper = YouTubeScraper()
    
    # Search for channels by keyword
    keyword = "tech review"
    channels = scraper.search_channels_by_keyword(keyword, max_results=5)
    
    print(f"Found {len(channels)} channels for keyword: {keyword}")
    
    # Get detailed information for each channel
    channel_data_list = []
    
    for channel_info in channels:
        print(f"\nProcessing: {channel_info['channel_name']}")
        
        # Get channel details
        details = scraper.get_channel_details(channel_info['channel_id'])
        if details:
            print(f"  Subscribers: {details['subscriber_count']:,}")
            print(f"  Videos: {details['video_count']:,}")
            print(f"  Views: {details['view_count']:,}")
            
            # Get some videos
            videos = scraper.get_channel_videos(channel_info['channel_id'], max_videos=3)
            print(f"  Recent videos: {len(videos)}")
            
            # Create channel data object
            channel_data = ChannelData(
                channel_id=details['channel_id'],
                channel_name=details['channel_name'],
                channel_url=details['channel_url'],
                description=details['description'],
                subscriber_count=details['subscriber_count'],
                video_count=details['video_count'],
                view_count=details['view_count'],
                country=details['country'],
                created_date=details['created_date'],
                keywords=channel_info['keywords'],
                scraped_at=datetime.now().isoformat()
            )
            
            channel_data_list.append(channel_data)
    
    # Export to CSV
    if channel_data_list:
        csv_filename = export_to_csv(channel_data_list, "example_channels.csv")
        print(f"\nExported {len(channel_data_list)} channels to {csv_filename}")
    else:
        print("No channels were processed successfully")

if __name__ == "__main__":
    example_usage()
