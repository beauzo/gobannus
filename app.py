import os
import sys
import asyncio
import logging
import datetime
import sqlite3
from uuid import uuid4, UUID
from enum import Enum
from typing import List
from dotenv import load_dotenv
from urllib.request import pathname2url

from ffmpeg import FFmpeg
from wakeonlan import send_magic_packet

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

from schema import RecordingModel

# from sqlalchemy.orm import Session

# from . import crud, model, schema
# from .database import SessionLocal, engine

# models.Base.metadata.create_all(bind=engine)

load_dotenv()

class CustomFormatter(logging.Formatter):
    debug_color = "\x1b[1;32m"      # green text
    info_color = "\x1b[38;20m"      # grey text
    warning_color = "\x1b[33;20m"   # yellow text
    error_color = "\x1b[31;20m"     # red text
    critical_color = "\x1b[41;30m"   # white text, red background
    reset = "\x1b[0m"
    format = "%(asctime)s %(levelname)s %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: debug_color + format + reset,
        logging.INFO: info_color + format + reset,
        logging.WARNING: warning_color + format + reset,
        logging.ERROR: error_color + format + reset,
        logging.CRITICAL: critical_color + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
logger.setLevel(os.environ.get('AIRPLANE_BUILD_TRACKER_LOGLEVEL', logging.INFO))


def get_env(env_var: str, default=None):
    try:
        env_var_value = os.environ[env_var]
    except KeyError:
        if default:
            return default

        logger.critical(f'{env_var} must be defined.')
        sys.exit(1)
    
    return env_var_value

camera_url = get_env('AIRPLANE_BUILD_TRACKER_CAMERA_URL')
logger.info(f'camera_url: {camera_url}')

camera_mac_address = get_env('AIRPLANE_BUILD_TRACKER_CAMERA_MAC_ADDRESS')
logger.info(f'camera_mac_address: {camera_mac_address}')

recordings_db_file = get_env('AIRPLANE_BUILD_TRACKER_DB_FILE', default='recordings.db')
logger.info(f'recordings_db_file: {recordings_db_file}')


RECORDINGS_DIR = 'recordings'
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
    logger.warn(f'created directory {RECORDINGS_DIR}')
else:
    logger.debug(f'{RECORDINGS_DIR} directory exists')


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


class RecordingStore():
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.db_uri = f'file:{pathname2url(self.db_file)}?mode=rw'
        
        try:
            logger.debug(f'attempting to open database file {self.db_uri}')
            sqlite3.connect(self.db_uri, uri=True)
        except sqlite3.OperationalError:
            # create the database file if it doesn't exist
            logger.debug(f'sqlite3 database file {self.db_file} not found')
            create_db_uri = 'file:{}?mode=rwc'.format(pathname2url(self.db_file))
            logger.debug(f'creating {create_db_uri}')
            db_conn = sqlite3.connect(create_db_uri, uri=True)

            # Initialize table schema
            with db_conn:
                logger.debug(f'creating RECORDING table')
                db_conn.execute('''
                    CREATE TABLE recording (
                        uuid text unique,
                        name text,
                        description text,
                        is_recording int,
                        progress text,
                        start_time timestamp,
                        stop_time timestamp,
                        output_file text
                    );
                ''')

            db_conn.close()

    def write_recording(self, recording: RecordingModel):
        logger.debug(f'RecordingStore.write_recording(): recording: {recording}')
        try:
            db_conn = sqlite3.connect(self.db_uri, uri=True)
            with db_conn:
                db_conn.execute('''
                        INSERT INTO recording(uuid, name, description,
                            is_recording, progress, start_time, stop_time, 
                            output_file)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(uuid) DO UPDATE SET
                                name=excluded.name,
                                description=excluded.description,
                                is_recording=excluded.is_recording,
                                progress=excluded.progress,
                                start_time=excluded.start_time,
                                stop_time=excluded.stop_time,
                                output_file=excluded.output_file;
                    ''',
                    (
                        str(recording.uuid),
                        recording.name,
                        recording.description,
                        int(recording.is_recording),
                        recording.progress,
                        recording.start_time,
                        recording.stop_time,
                        recording.output_file
                    )
                )
        except sqlite3.IntegrityError:
            logger.error('Unable to write recording to database')
        finally:
            db_conn.close()

    def read_recording(self, uuid: UUID) -> RecordingModel:
        recording = None
        db_conn = sqlite3.connect(self.db_uri, uri=True)
        with db_conn:
            db_recording = db_conn.execute('''
                    SELECT * FROM recording WHERE uuid=:uuid LIMIT 1
                ''', {'uuid': str(uuid)}).fetchone()

            logger.debug(db_recording)

            if db_recording:
                recording = RecordingModel(
                    uuid=UUID(db_recording[0]),
                    name=db_recording[1],
                    description=db_recording[2],
                    is_recording=bool(db_recording[3]),
                    progress=db_recording[4],
                    start_time=db_recording[5],
                    stop_time=db_recording[6],
                    output_file=db_recording[7]
                )

        db_conn.close()

        return recording


    def get_recordings(self) -> list:
        db_conn = sqlite3.connect(self.db_uri, uri=True)
        with db_conn:
            recordings = db_conn.execute('''
                    SELECT * FROM recording;
                ''').fetchall()

            for r in recordings:
                logger.debug(r)

        db_conn.close()

        # return [
        #     RecordingModel(
        #         uuid=self.uuid,
        #         name=self.name,
        #         description=self.description,
        #         is_recording=self.is_recording,
        #         progress=str(self.progress),
        #         start_time=self.start_time,
        #         stop_time=self.stop_time,
        #         output_file=self.output_file
        #     )
        # ]


class Recording():
    def __init__(self, store: RecordingStore):
        self.ffmpeg = None
        self.file_index = 0
        self.n_errors = 0
        self.store = store
        # self.model = RecordingModel(uuid=uuid4())
        self.model = RecordingModel()
        logger.debug(f'Recording.__init__(): {self.model}')
        self.set_model(self.model)

    async def start(self):
        while True:
            # send "magic" wake-on-LAN packet before recording
            logger.info('sending "magic" WOL packet')
            send_magic_packet(camera_mac_address)

            # wait for a few seconds for the WOL packet to take effect (TBD: replace with a ping?)
            logger.info('waiting for WOL to take effect...')
            await asyncio.sleep(1)

            self.set_output_file(f'./{RECORDINGS_DIR}/{str(self.model.uuid)}_{self.file_index}.mp4')

            # ffmpeg -i "<camera_url>" -an -vf framestep=4,setpts=N/60/TB,fps=60 <output>
            ffmpeg = FFmpeg().input(
                camera_url,
                
                # Specify file options using kwargs
                rtsp_transport='tcp',
                rtsp_flags='prefer_tcp',

            ).option('an').option('y').output(
                self.get_output_file(),
                # Use a dictionary when an option name contains special characters
                {
                    'filter:v': "framestep=4,setpts=N/60/TB,fps=60,drawtext=fontfile=roboto.ttf:fontsize=36:fontcolor=yellow:text='%{localtime}'",
                    'vcodec': 'libx265',
                    'crf': 28,
                    'tag:v': 'hvc1',
                },
                flush_packets=1,
            )

            @ffmpeg.on('start')
            def on_start(arguments):
                logger.info(f'ffmpeg start: arguments: {arguments}')
                self.set_is_recording(True)
                self.set_start_time(datetime.datetime.now())

            @ffmpeg.on('stderr')
            def on_stderr(line):
                logger.info(f'ffmpeg ffmpeg: {line}')

            @ffmpeg.on('progress')
            def on_progress(progress):
                logger.debug(f'ffmpeg progress: {progress}')
                self.set_progress(str(progress))

            @ffmpeg.on('completed')
            def on_completed():
                logger.warn('ffmpeg completed: on its own')

            @ffmpeg.on('terminated')
            def on_terminated():
                logger.info('ffmpeg terminated')
                self.set_is_recording(False)
                self.set_stop_time(datetime.datetime.now())

            @ffmpeg.on('error')
            def on_error(code):
                logger.error(f'ffmpeg error: {code}')
                self.n_errors += 1

            self.ffmpeg = ffmpeg

            # Start recording
            await ffmpeg.execute()

            self.ffmpeg = None
            self.file_index += 1

            if not self.get_is_recording():
                break

    def stop(self):
        if self.ffmpeg:
            self.ffmpeg.terminate()

    def _read(self):
        self.model = self.get_model()

    def _write(self):
        self.store.write_recording(self.model)

    def get_model(self) -> RecordingModel:
        return self.store.read_recording(self.model.uuid)

    def set_model(self, recording_model: RecordingModel):
        self.store.write_recording(recording_model)

    def get_uuid(self) -> UUID:
        self._read()
        return self.model.uuid

    def get_name(self) -> str:
        self._read()
        return self.model.name

    def set_name(self, name: str):
        self.model.name = name
        self._write()

    def get_description(self) -> str:
        self._read()
        return self.model.description

    def set_description(self, description: str):
        self.model.description = description
        self._write()

    def get_is_recording(self) -> bool:
        self._read()
        return self.model.is_recording

    def set_is_recording(self, is_recording: bool):
        self.model.is_recording = is_recording
        self._write()

    def get_progress(self) -> str:
        self._read()
        return self.model.progress

    def set_progress(self, progress: str):
        self.model.progress = progress
        self._write()

    def get_start_time(self) -> datetime.datetime:
        self._read()
        return self.model.start_time

    def set_start_time(self, start_time: datetime.datetime):
        self.model.start_time = start_time
        self._write()

    def get_stop_time(self) -> datetime.datetime:
        self._read()
        return self.model.stop_time

    def set_stop_time(self, stop_time: datetime.datetime):
        self.model.stop_time = stop_time
        self._write()

    def get_output_file(self) -> str:
        self._read()
        return self.model.output_file

    def set_output_file(self, output_file: str):
        self.model.output_file = output_file
        self._write()


recordings_store = RecordingStore(recordings_db_file)
recordings = {}

app = FastAPI()


@app.get('/recording', response_model=List[RecordingModel])
def get_recordings():
    recordings_store.get_recordings()

    return [recording.get_model() for recording in recordings.values()]


@app.get('/recording/{recording_uuid}', response_class=FileResponse)
def get_recording(recording_uuid: UUID):
    if recording_uuid not in recordings:
        raise HTTPException(status_code=404, detail=f"Recording {recording_uuid} not found.")

    video_file = f'./{RECORDINGS_DIR}/{str(recording_uuid)}.mp4'
    if os.path.exists(video_file):
        return video_file
    else:
        raise HTTPException(status_code=404, detail=f'Video file {video_file} not found.')


async def start_ffmepg(recording: Recording):
    logger.debug('before: await recording.start()')
    await recording.start()
    logger.debug('after: await recording.start()')


@app.post('/recording')
def create_recording(recording_data: RecordingModel, background_tasks: BackgroundTasks):
    new_recording = Recording(recordings_store)
    new_recording.set_name(recording_data.name)
    new_recording.set_description(recording_data.description)
    
    recordings[new_recording.get_uuid()] = new_recording

    # start the ffmpeg recording process
    background_tasks.add_task(start_ffmepg, new_recording)

    return new_recording.get_model()


@app.patch('/recording/{recording_uuid}')
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


@app.delete('/recordings/{recording_uuid}')
def delete_recording(recording_uuid):
    logger.debug(f'recording_uuid: {recording_uuid}')
    return {'success': True}
