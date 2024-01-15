import os
from uuid import UUID
from typing import List, Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

from .env import get_env
from .logger import get_logger
from .camera import Camera
from .schema import RecordingModel
from .store import RecordingStore
from .recording import Recording

# from sqlalchemy.orm import Session

# from . import crud, model, schema
# from .database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)

print(f"{__name__} loaded")
logger = get_logger(__name__)

RECORDINGS_DIR = "recordings"
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
    logger.warn(f"created directory {RECORDINGS_DIR}")
else:
    logger.debug(f"{RECORDINGS_DIR} directory exists")

camera_url = get_env("AIRPLANE_BUILD_TRACKER_CAMERA_URL")
logger.info(f"camera_url: {camera_url}")

camera_mac_address = get_env("AIRPLANE_BUILD_TRACKER_CAMERA_MAC_ADDRESS")
logger.info(f"camera_mac_address: {camera_mac_address}")

recordings_db_file = get_env("AIRPLANE_BUILD_TRACKER_DB_FILE", default="recordings.db")
logger.info(f"recordings_db_file: {recordings_db_file}")

default_camera = Camera(camera_url, camera_mac_address)

recordings_store = RecordingStore(recordings_db_file)
recordings: Dict[UUID, Recording] = {}

print(Recording(recordings_store, default_camera, RECORDINGS_DIR))
print(Recording(recordings_store, default_camera, RECORDINGS_DIR))

app = FastAPI()


@app.get("/recording", response_model=List[RecordingModel])
def get_recordings():
    recordings_store.get_recordings()

    return [recording.get_model() for recording in recordings.values()]


@app.get("/recording/{recording_uuid}", response_class=FileResponse)
def get_recording(recording_uuid: UUID):
    if recording_uuid not in recordings:
        raise HTTPException(
            status_code=404, detail=f"Recording {recording_uuid} not found."
        )

    video_file = f"./{RECORDINGS_DIR}/{str(recording_uuid)}.mp4"
    if os.path.exists(video_file):
        return video_file
    else:
        raise HTTPException(
            status_code=404, detail=f"Video file {video_file} not found."
        )


async def start_ffmepg(recording: Recording):
    logger.debug("before: await recording.start()")
    await recording.start()
    logger.debug("after: await recording.start()")


@app.post("/recording")
def create_recording(recording_data: RecordingModel, background_tasks: BackgroundTasks):
    new_recording = Recording(recordings_store, default_camera, RECORDINGS_DIR)
    new_recording.set_name(recording_data.name)
    new_recording.set_description(recording_data.description)

    logger.info(f"/recording: created new recording {new_recording.get_uuid()}")

    recordings[new_recording.get_uuid()] = new_recording

    # start the ffmpeg recording process
    background_tasks.add_task(start_ffmepg, new_recording)

    return new_recording.get_model()


@app.patch("/recording/{recording_uuid}")
def modify_recording(recording_uuid: UUID, recording_data: RecordingModel):
    if recording_uuid not in recordings:
        raise HTTPException(status_code=404, detail="Recording not found.")

    recording = recordings[recording_uuid]

    # Stop recording
    if recording_data.is_recording is False:
        recording.stop()

    if recording_data.name:
        recording.set_name(recording_data.name)
    if recording_data.description:
        recording.set_description(recording_data.description)

    return recording.get_model()


@app.delete("/recordings/{recording_uuid}")
def delete_recording(recording_uuid):
    logger.debug(f"recording_uuid: {recording_uuid}")
    return {"success": True}
