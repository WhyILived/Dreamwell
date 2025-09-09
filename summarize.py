import os
from typing import Optional
from datetime import datetime
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

# ======= Config =======
API_KEY = "tlk_3WMDD6H1KM6HTQ2847RF73VWDCGY"
ENGINE = "pegasus1.2"
LANGUAGE = "en"
INDEX_NAME = "chatgpt_index"
# ======================

client = TwelveLabs(api_key=API_KEY)


def get_or_create_index(index_name: str):
    """
    Retrieves the TwelveLabs index by name, or creates it if it doesn't exist.
    """
    for index in client.index.list():
        if index.name == index_name:
            return index

    return client.index.create(
        name=index_name,
        models=[{
            "name": ENGINE,
            "options": ["visual", "audio"]
        }]
    )


def get_existing_video_id(index_id: str, filename: str) -> Optional[str]:
    """
    Checks if the given video file is already indexed and returns its video ID.
    """
    tasks = client.task.list(index_id=index_id)
    base_filename = os.path.basename(filename)

    print(f"🔍 Looking for existing uploaded video matching: {base_filename}")

    matching_tasks = [
        task for task in tasks
        if task.status == "ready" and task.system_metadata
        and os.path.basename(task.system_metadata.get("filename", "")) == base_filename
    ]

    if matching_tasks:
        matching_tasks.sort(
            key=lambda t: datetime.fromisoformat(t.created_at.rstrip("Z"))
        )
        latest_task = matching_tasks[-1]
        print(f"✅ Found existing video: {latest_task.system_metadata['filename']} (video_id={latest_task.video_id})")
        return latest_task.video_id

    return None


def summarize_video(file_path: str) -> str:
    """
    Uploads a video to TwelveLabs if not already indexed,
    and returns the combined summary and chapter text.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"❌ Video file not found: {file_path}")

    index = get_or_create_index(INDEX_NAME)
    video_id = get_existing_video_id(index.id, file_path)

    if not video_id:
        print("📤 Uploading and indexing video...")
        task = client.task.create(index_id=index.id, file=file_path)
        task.wait_for_done()

        if task.status != "ready":
            raise RuntimeError(f"❌ Indexing failed (status: {task.status})")

        video_id = task.video_id
        print(f"✅ Video indexed successfully: video_id={video_id}")
    else:
        print(f"✅ Using previously indexed video: video_id={video_id}")

    # Generate Summary
    print("\n📄 Generating summary...")
    res_summary = client.summarize(video_id=video_id, type="summary")
    summary_text = f"\n🔹 Summary:\n{res_summary.summary}"

    # Generate Chapters
    print("\n📑 Generating chapters...")
    res_chapters = client.summarize(video_id=video_id, type="chapter")

    chapter_texts = []
    for chapter in res_chapters.chapters:
        chapter_texts.append(
            f"\n🔸 Chapter {chapter.chapter_number}\n"
            f"Start: {chapter.start}, End: {chapter.end}\n"
            f"Title: {chapter.chapter_title}\n"
            f"Summary: {chapter.chapter_summary}"
        )

    combined_text = summary_text + "\n" + "\n".join(chapter_texts)
    return combined_text