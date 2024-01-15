import sqlite3
from uuid import UUID
from urllib.request import pathname2url
from .logger import get_logger
from .schema import RecordingModel

print(f'{__name__} loaded')
logger = get_logger(__name__)


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
                        uuid text NOT NULL PRIMARY KEY,
                        name text,
                        description text,
                        is_recording int NOT NULL DEFAULT 0,
                        progress text,
                        start_time timestamp,
                        stop_time timestamp,
                        output_file text
                    );
                ''')

                db_conn.execute('''
                    CREATE TABLE recording_file (
                        filename text NOT NULL PRIMARY KEY,
                        recording_uuid REFERENCES recording
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

    def read_recording(self, recording_uuid: UUID) -> RecordingModel:
        recording = None
        db_conn = sqlite3.connect(self.db_uri, uri=True)
        with db_conn:
            db_recording = db_conn.execute('''
                    SELECT * FROM recording WHERE uuid=:uuid LIMIT 1
                ''', {'uuid': str(recording_uuid)}).fetchone()

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

    def add_recording_file(self, recording_uuid: UUID, recording_file: str):
        logger.debug(f'RecordingStore.add_recording_file(): recording_uuid: {recording_uuid}, recording_file: {recording_file}')
        try:
            db_conn = sqlite3.connect(self.db_uri, uri=True)
            with db_conn:
                db_conn.execute('''
                        INSERT INTO recording_file(filename, recording_uuid)
                            VALUES (?, ?)
                            ON CONFLICT(filename) DO UPDATE SET
                                recording_uuid=excluded.recording_uuid
                    ''',
                    (
                        recording_file,
                        str(recording.uuid)
                    )
                )
        except sqlite3.IntegrityError:
            logger.error('Unable to write recording file to database')
        finally:
            db_conn.close()
