import datetime
from uuid import uuid4, UUID
from typing import Union
from pydantic import BaseModel, UUID4

class RecordingModel(BaseModel):
    uuid: Union[UUID, None] = uuid4()
    name: Union[str, None] = None
    description: Union[str, None] = None
    is_recording: Union[bool, None] = False
    progress: Union[str, None] = None
    start_time: Union[datetime.datetime, None] = None
    stop_time: Union[datetime.datetime, None] = None
    output_file: Union[str, None] = None

    class Config:
        orm_mode = True
