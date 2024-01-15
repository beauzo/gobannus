import os
import asyncio
import datetime
from uuid import UUID
from ffmpeg import FFmpeg
from wakeonlan import send_magic_packet
from .logger import get_logger
from .store import RecordingStore
from .schema import RecordingModel
from .camera import Camera

print(f'{__name__} loaded')
logger = get_logger(__name__)


class Recording():
    def __init__(self, store: RecordingStore, camera: Camera, recordings_dir: str):
        self.ffmpeg = None
        self.file_index = 0
        self.n_errors = 0
        self.store = store
        self.camera = camera
        self.recordings_dir = recordings_dir
        self.model = RecordingModel()
        logger.debug(f'Recording.__init__(): {self.model}')
        self.set_model(self.model)

    async def start(self):
        while True:
            # send "magic" wake-on-LAN packet before recording
            logger.info(f'sending "magic" WOL packet to {self.camera.mac_address}')
            send_magic_packet(self.camera.mac_address)

            # wait for a few seconds for the WOL packet to take effect (TBD: replace with a ping?)
            logger.info('waiting for WOL to take effect...')
            await asyncio.sleep(1)

            self.set_output_file(os.path.abspath(f'./{self.recordings_dir}/{str(self.model.uuid)}-{self.file_index}.mp4'))

            # ffmpeg -i "<camera_url>" -an -vf framestep=4,setpts=N/60/TB,fps=60 <output>
            ffmpeg = FFmpeg().input(
                self.camera.url,
                
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
