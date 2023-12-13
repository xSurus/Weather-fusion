from pydantic import BaseModel, Field
import datetime
from typing import Union
from enum import Enum


class RecordType(str, Enum):
    owner = "init"
    member = "radar"
    invited = "prediction"


class RainRecord(BaseModel):
    record_id:  Field(alias='_id')
    dt: datetime.datetime
    type: RecordType
    version: Union[None, datetime.datetime] = None
    processed: bool = False
