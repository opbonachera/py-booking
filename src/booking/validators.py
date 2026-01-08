"""Validators for booking operations"""
from datetime import datetime
from typing import Tuple
from booking.models.book import Booking

class DateValidator:
    """Validates dates for bookings"""
    
    DATE_FORMAT = "%Y-%m-%d"
    
    @staticmethod
    def is_valid_date_format(date_str: str) -> bool:
        """Check if date string is in valid format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, DateValidator.DATE_FORMAT)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date string to datetime object"""
        return datetime.strptime(date_str, DateValidator.DATE_FORMAT)
    
    @staticmethod
    def is_not_in_past(date_str: str) -> bool:
        """Check if date is not in the past"""
        date = DateValidator.parse_date(date_str)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return date >= today
    
    @staticmethod
    def is_start_before_end(start_str: str, end_str: str) -> bool:
        """Check if start date is before end date"""
        start = DateValidator.parse_date(start_str)
        end = DateValidator.parse_date(end_str)
        return start < end


class BookingValidator:
    """Validates booking conflicts"""
    
    @staticmethod
    def has_overlap(booking1: Booking, booking2: Booking) -> bool:
        """Check if two bookings have overlapping dates"""
        start1 = datetime.strptime(booking1.start_date, DateValidator.DATE_FORMAT)
        end1 = datetime.strptime(booking1.end_date, DateValidator.DATE_FORMAT)
        start2 = datetime.strptime(booking2.start_date, DateValidator.DATE_FORMAT)
        end2 = datetime.strptime(booking2.end_date, DateValidator.DATE_FORMAT)
        
        # No overlap if one booking ends before the other starts
        return not (end1 <= start2 or end2 <= start1)
    
    @staticmethod
    def check_room_availability(
        room_id: str, 
        start_date: str, 
        end_date: str, 
        existing_bookings: list[Booking]
    ) -> Tuple[bool, str]:
        """Check if room is available for the given dates"""
        new_booking = Booking(
            id="temp",
            room_name="",
            room_id=room_id,
            start_date=start_date,
            end_date=end_date
        )
        
        for booking in existing_bookings:
            if booking.room_id == room_id and BookingValidator.has_overlap(new_booking, booking):
                return False, f"Room is already booked from {booking.start_date} to {booking.end_date}"
        
        return True, ""
    
    @staticmethod
    def validate_booking_dates(start_date: str, end_date: str) -> Tuple[bool, str]:
        """Validate booking dates comprehensively"""
        # Check format
        if not DateValidator.is_valid_date_format(start_date):
            return False, "Invalid start date format. Use YYYY-MM-DD"
        
        if not DateValidator.is_valid_date_format(end_date):
            return False, "Invalid end date format. Use YYYY-MM-DD"
        
        # Check dates are not in past
        if not DateValidator.is_not_in_past(start_date):
            return False, "Start date cannot be in the past"
        
        if not DateValidator.is_not_in_past(end_date):
            return False, "End date cannot be in the past"
        
        # Check start is before end
        if not DateValidator.is_start_before_end(start_date, end_date):
            return False, "Start date must be before end date"
        
        return True, ""
