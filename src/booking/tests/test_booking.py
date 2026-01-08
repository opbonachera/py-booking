"""Test suite for booking functionality"""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from typer.testing import CliRunner

from booking import __app_name__, __version__, SUCCESS
from booking.cli import app
from booking.models.book import Booking, BookingService, BookServiceResponse
from booking.validators import DateValidator, BookingValidator
from booking.database import DatabaseHandler

runner = CliRunner()


# ============================================================================
# CLI Tests
# ============================================================================

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

# ============================================================================
# Integration Tests
# ============================================================================

class TestBookingIntegration:
    """Integration tests for the booking system"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"rooms": [], "bookings": []}, f)
            db_path = Path(f.name)
        
        yield db_path
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    def test_complete_booking_workflow(self, temp_db):
        """Test complete booking workflow with validation"""
        service = BookingService(temp_db)
        
        # Future dates
        start_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        
        # Validate dates
        is_valid, msg = BookingValidator.validate_booking_dates(start_date, end_date)
        assert is_valid
        
        # Check availability
        existing_bookings = service.get_bookings_by_room("room-1").list
        is_available, msg = BookingValidator.check_room_availability(
            "room-1", start_date, end_date, existing_bookings
        )
        assert is_available
        
        # Add booking
        response = service.add("Room A", "room-1", start_date, end_date)
        assert response.error == SUCCESS
        
        # Verify booking was added
        all_bookings = service.get_bookings()
        assert len(all_bookings.list) == 1
    
    def test_prevent_overlapping_bookings(self, temp_db):
        """Test that overlapping bookings are detected"""
        service = BookingService(temp_db)
        
        # Add first booking
        service.add("Room A", "room-1", "2026-01-10", "2026-01-15")
        
        # Try to book overlapping dates
        existing_bookings = service.get_bookings_by_room("room-1").list
        is_available, msg = BookingValidator.check_room_availability(
            "room-1", "2026-01-12", "2026-01-18", existing_bookings
        )
        
        assert not is_available
        assert "already booked" in msg
    
    def test_multiple_bookings_same_room(self, temp_db):
        """Test multiple non-overlapping bookings for the same room"""
        service = BookingService(temp_db)
        
        # Add first booking
        service.add("Room A", "room-1", "2026-01-10", "2026-01-15")
        
        # Add second booking with no overlap
        service.add("Room A", "room-1", "2026-01-15", "2026-01-20")
        
        # Verify both bookings exist
        room_bookings = service.get_bookings_by_room("room-1").list
        assert len(room_bookings) == 2
    
    def test_book_different_rooms_same_dates(self, temp_db):
        """Test booking different rooms for the same dates"""
        service = BookingService(temp_db)
        
        # Book same dates for different rooms
        service.add("Room A", "room-1", "2026-01-10", "2026-01-15")
        service.add("Room B", "room-2", "2026-01-10", "2026-01-15")
        
        # Verify both bookings exist
        all_bookings = service.get_bookings()
        assert len(all_bookings.list) == 2
        
        room1_bookings = service.get_bookings_by_room("room-1").list
        room2_bookings = service.get_bookings_by_room("room-2").list
        
        assert len(room1_bookings) == 1
        assert len(room2_bookings) == 1
    
    def test_booking_persistence_across_instances(self, temp_db):
        """Test that bookings persist across different service instances"""
        # First instance: add bookings
        service1 = BookingService(temp_db)
        service1.add("Room A", "room-1", "2026-01-10", "2026-01-15")
        service1.add("Room B", "room-2", "2026-02-10", "2026-02-15")
        
        # Second instance: verify bookings exist
        service2 = BookingService(temp_db)
        all_bookings = service2.get_bookings()
        
        assert len(all_bookings.list) == 2
        
        # Third instance: add more bookings
        service3 = BookingService(temp_db)
        service3.add("Room C", "room-3", "2026-03-10", "2026-03-15")
        
        # Fourth instance: verify all bookings
        service4 = BookingService(temp_db)
        all_bookings = service4.get_bookings()
        assert len(all_bookings.list) == 3