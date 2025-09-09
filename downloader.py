import yt_dlp
import os

def download_video(url: str, output_path: str = ".") -> str:
    """
    Downloads the YouTube video and returns the actual full path to the saved file.
    """
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegMetadata'}],
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # This returns the actual filename written to disk
        return ydl.prepare_filename(info)

