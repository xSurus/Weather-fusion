from pydantic import BaseModel, Field
import datetime
from typing import Union
from enum import Enum


class RecordType(str, Enum):
    owner = "init"
    member = "radar"
    invited = "prediction"


class RainRecord(BaseModel):
    record_id: Union[None, str] = Field(alias='_id', default=None)
    dt: datetime.datetime
    type: RecordType
    version: Union[None, datetime.datetime] = None
    processed: bool = False
