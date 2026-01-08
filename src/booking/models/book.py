""" Booking model-controller"""
import uuid
from booking import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, ERROR_ELEMENT_NOT_FOUND
from typing import Any, Dict, NamedTuple
from datetime import datetime
from pathlib import Path
from booking.database import DatabaseHandler
from dataclasses import dataclass
from booking import database

class BookServiceResponse(NamedTuple):
    booking: 'Booking' = None
    list: list['Booking'] = None
    error: int = SUCCESS

@dataclass
class Booking():
    id: str
    room_name: str
    room_id: str
    start_date: str
    end_date: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "room_name": self.room_name,
            "room_id": self.room_id,
            "start_date": self.start_date,
            "end_date": self.end_date
        }

class BookingService():
    
    def __init__(self, db_path: Path):
        self._db_handler = database.DatabaseHandler(db_path)
    
    def get_bookings(self) -> BookServiceResponse:
        """Get all bookings from database"""
        read = self._db_handler.read("bookings")
        
        if read.code != SUCCESS:
            return BookServiceResponse(list=[], error=read.code)
        
        bookings = [
            Booking(
                id=booking.get("id", ""),
                room_name=booking.get("room_name", ""),
                room_id=booking.get("room_id", ""),
                start_date=booking.get("start_date", ""),
                end_date=booking.get("end_date", "")
            )
            for booking in read.list
        ]
        
        return BookServiceResponse(list=bookings, error=SUCCESS)
    
    def get_bookings_by_room(self, room_id: str) -> BookServiceResponse:
        """Get all bookings for a specific room"""
        response = self.get_bookings()
        
        if response.error != SUCCESS:
            return response
        
        room_bookings = [b for b in response.list if b.room_id == room_id]
        return BookServiceResponse(list=room_bookings, error=SUCCESS)
    
    def add(self, room_name: str, room_id: str, start_date: str, end_date: str) -> BookServiceResponse:
        """Add a new booking"""
        booking = Booking(
            id=str(uuid.uuid4()),
            room_name=room_name,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get all existing bookings
        response = self.get_bookings()
        if response.error != SUCCESS:
            bookings = []
        else:
            bookings = response.list
        
        # Add new booking
        bookings_data = [b.to_dict() for b in bookings] + [booking.to_dict()]
        
        write_response = self._db_handler.write("bookings", bookings_data)
        
        if write_response.code != SUCCESS:
            return BookServiceResponse(error=write_response.code)
        
        return BookServiceResponse(booking=booking, error=SUCCESS)