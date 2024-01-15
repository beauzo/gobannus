from uuid import UUID
from sqlalchemy.orm import Session

from . import model, schema


def get_recording(db: Session, uuid: UUID):
    return (
        db.query(models.RecordingModel)
        .filter(models.RecordingModel.uuid == uuid)
        .first()
    )


def create_recording(db: Session, recording: schemas.RecordingModel):
    db_recording = models.RecordingModel(
        name=recording.name,
        description=recording.description,
        is_recording=recording.is_recording,
        progress=recording.progress,
        start_time=recording.start_time,
        stop_time=recording.stop_time,
        output_file=recording.output_file,
    )

    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)

    return db_recording
