import uuid
from sqlalchemy import Boolean, Column, DateTime, Field, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


def uuid_gen():
    return str(uuid.uuid4())


class RecordingModel(Base):
    __tablename__ = "recording"

    id = Column(String, primary_key=True, index=True, default=uuid_gen)
    name = Column(String)
    description = Column(String)
    is_recording = Column(Boolean, default=False)
    progress = Column(String)
    start_time = Column(DateTime)
    stop_time = Column(DateTime)
    output_file = Column(String)
