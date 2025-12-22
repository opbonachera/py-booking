""" Booking model-controller"""
import uuid
from booking import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS
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
    


@dataclass
class Room():
    id: int
    name: str
    capacity: int
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "capacity": self.capacity
        }

@dataclass
class RoomServiceResponse():
    list: list[Room]
    error: str
    
class RoomService():
        
    def __init__(self, db_path: Path):
        self._db_handler = DatabaseHandler(db_path)
    
    def get_rooms(self)->list[Room]:
        read = self._db_handler.read("rooms")
        if read.code == DB_READ_ERROR:
            return RoomServiceResponse([], read.error)
        
        return RoomServiceResponse(read.list, SUCCESS)
        
    def add(self, name: str, capacity: int)->Room:
        name += ('.' if not name.endswith('.') else '').capitalize()
        capacity = capacity if capacity > -1 else 'not informed'
        
        room = Room(
            uuid.uuid4(),
            name,
            capacity
        )
        
        room_list = self._db_handler.read("rooms").list
        if room_list.code == DB_READ_ERROR:
            return RoomServiceResponse(room, room_list.error)
        
        room_list.append(room.to_dict())
        
        self._db_handler.write("rooms", room_list)
        
        return RoomServiceResponse(room, SUCCESS)