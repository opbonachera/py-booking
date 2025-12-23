""" Booking model-controller"""
import uuid
from booking import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, ERROR_ELEMENT_NOT_FOUND, DUPLICATED_ROOM_NAME
from typing import Any, Dict, NamedTuple
from datetime import datetime
from pathlib import Path
from booking.database import DatabaseHandler
from dataclasses import dataclass

@dataclass
class Book():
    id: int
    room_id: int
    start: datetime
    end: datetime