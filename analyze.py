import os
from typing import Optional
from datetime import datetime
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

# ======= Config =======
API_KEY = ""
ENGINE = "pegasus1.2"
LANGUAGE = "en"
INDEX_NAME = "chatgpt_index"
# ======================

client = TwelveLabs(api_key=API_KEY)
prompt = """Analyze this video for gameplay downtime events. Specifically:

Identify and return all time segments where the player is:

Eliminated / killed / dies

In a "death screen", spectator mode, or report screen

Waiting to respawn

Viewing death summaries or kill cam

For each death/downtime event:

Return the start and end timestamps

Include any visible text such as:

"report"

"you are dead"

"respawning in" or similar

Indicate if the screen has a grayscale effect, red tint, or other visual indicator

Identify loading screens, including:

Matchmaking wait screens

Round transitions or pre-game loadouts

Black screens with logos or rotating animations

Identify and return:

Periods of visual inactivity (no player motion, HUD only, waiting states)

UI overlays that indicate player is not active (e.g., menus, scoreboards)

For each segment, return:

The timestamp

The reason (e.g., "death", "loading", "idle", "respawn wait")

Any visible keywords or UI elements

If possible, extract a thumbnail image or text snapshot from that frame
"""

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


def analyze_video(file_path: str) -> str:
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

    # Generate Analyze
    print("\n📄 Generating analyze...")
    res_summary = client.analyze(video_id=video_id, prompt=prompt)
    summary_text = f"\n🔹 Summary:\n{res_summary.data}"

    return summary_text

# Video goes here
print(analyze_video("./videos/VALORANT.mp4"))