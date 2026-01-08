import json
import pytest
from pathlib import Path
from typing import Any

from booking.models.room import Room, RoomService, RoomServiceResponse
from booking import SUCCESS, ERROR_ELEMENT_NOT_FOUND, DUPLICATED_ROOM_NAME


# ========== TEST DATA ==========
ROOM_CASES = [
    {"name": "the great salon", "capacity": 250},
    {"name": "macacha güemes", "capacity": 50},
    {"name": "cozy corner", "capacity": 10},
]


# ========== TEST: ADD ROOM ==========
@pytest.mark.parametrize("room", ROOM_CASES)
def test_add_room_persists_room(json_db: Path, room: dict[str, Any]):
    """Test that adding a room persists it to the database."""
    # Arrange
    service = RoomService(json_db)

    # Act
    response = service.add(room["name"], room["capacity"])

    # Assert
    assert response.error == SUCCESS
    assert isinstance(response.list, Room)
    assert response.list.name.lower() == room["name"].lower()
    assert response.list.capacity == room["capacity"]
    
    # Verify persistence
    room_list = service._db_handler.read("rooms").list
    assert len(room_list) == 1
    assert room_list[0]["name"].lower() == room["name"].lower()
    assert room_list[0]["capacity"] == room["capacity"]


def test_add_room_with_duplicate_name_fails(json_db: Path):
    """Test that adding a room with duplicate name returns error."""
    # Arrange
    service = RoomService(json_db)
    room_name = "the great salon"
    
    # Act
    first_add = service.add(room_name, 250)
    second_add = service.add(room_name, 300)
    
    # Assert
    assert first_add.error == SUCCESS
    assert second_add.error == DUPLICATED_ROOM_NAME
    assert len(service._db_handler.read("rooms").list) == 1


def test_add_room_formats_name_correctly(json_db: Path):
    """Test that room names are formatted with capitalize and end with period."""
    # Arrange
    service = RoomService(json_db)
    
    # Act
    response = service.add("my room", 50)
    
    # Assert
    assert response.list.name == "My room."


def test_add_room_with_negative_capacity(json_db: Path):
    """Test that adding a room with negative capacity sets it as 'not informed'."""
    # Arrange
    service = RoomService(json_db)
    
    # Act
    response = service.add("my room", -5)
    
    # Assert
    assert response.error == SUCCESS
    assert response.list.capacity == "not informed"


def test_add_multiple_rooms(json_db: Path):
    """Test adding multiple rooms."""
    # Arrange
    service = RoomService(json_db)
    rooms = [
        {"name": "room a", "capacity": 100},
        {"name": "room b", "capacity": 50},
        {"name": "room c", "capacity": 25},
    ]
    
    # Act
    for room in rooms:
        service.add(room["name"], room["capacity"])
    
    # Assert
    room_list = service._db_handler.read("rooms").list
    assert len(room_list) == 3


# ========== TEST: GET ROOMS ==========
def test_get_rooms_returns_empty_list_on_empty_db(json_db: Path):
    """Test that getting rooms from empty database returns empty list."""
    # Arrange
    service = RoomService(json_db)
    
    # Act
    response = service.get_rooms()
    
    # Assert
    assert response.error == SUCCESS
    assert response.list == []


def test_get_rooms_returns_all_rooms(json_db: Path):
    """Test that getting rooms returns all stored rooms."""
    # Arrange
    service = RoomService(json_db)
    rooms = [
        {"name": "room a", "capacity": 100},
        {"name": "room b", "capacity": 50},
    ]
    
    for room in rooms:
        service.add(room["name"], room["capacity"])
    
    # Act
    response = service.get_rooms()
    
    # Assert
    assert response.error == SUCCESS
    assert len(response.list) == 2


# ========== TEST: GET ROOM BY NAME ==========
def test_get_room_by_name_found(json_db: Path):
    """Test getting an existing room by name."""
    # Arrange
    service = RoomService(json_db)
    service.add("test room", 50)
    
    # Act
    response = service.get_room_by_name("test room")
    
    # Assert
    assert response.error == SUCCESS
    assert len(response.list) == 1
    assert response.list[0]["name"].lower() == "test room"


def test_get_room_by_name_case_insensitive(json_db: Path):
    """Test that getting room by name is case-insensitive."""
    # Arrange
    service = RoomService(json_db)
    service.add("Test Room", 50)
    
    # Act
    response_lower = service.get_room_by_name("test room")
    response_upper = service.get_room_by_name("TEST ROOM")
    response_mixed = service.get_room_by_name("TeSt RoOm")
    
    # Assert
    assert response_lower.error == SUCCESS
    assert response_upper.error == SUCCESS
    assert response_mixed.error == SUCCESS


def test_get_room_by_name_not_found(json_db: Path):
    """Test getting a non-existing room by name."""
    # Arrange
    service = RoomService(json_db)
    service.add("room a", 50)
    
    # Act
    response = service.get_room_by_name("non-existent room")
    
    # Assert
    assert response.error == ERROR_ELEMENT_NOT_FOUND
    assert response.list == []


# ========== TEST: EDIT ROOM ==========
def test_edit_room_updates_name_and_capacity(json_db: Path):
    """Test editing both name and capacity of a room."""
    # Arrange
    service = RoomService(json_db)
    service.add("original room", 50)
    
    # Act
    response = service.edit("Original room.", "new room", 100)
    
    # Assert
    assert response.error == SUCCESS
    assert response.list["name"] == "new room"
    assert response.list["capacity"] == 100


def test_edit_room_preserves_name_if_not_provided(json_db: Path):
    """Test that editing without name keeps original name."""
    # Arrange
    service = RoomService(json_db)
    service.add("room name", 50)
    
    # Act
    response = service.edit("Room name.", "", 100)
    
    # Assert
    assert response.error == SUCCESS
    assert response.list["name"] == "Room name."


def test_edit_room_preserves_capacity_if_not_provided(json_db: Path):
    """Test that editing without capacity keeps original capacity."""
    # Arrange
    service = RoomService(json_db)
    service.add("room name", 50)
    
    # Act
    response = service.edit("Room name.", "new name", 0)
    
    # Assert
    assert response.error == SUCCESS
    assert response.list["capacity"] == 50


def test_edit_room_not_found(json_db: Path):
    """Test editing a non-existing room."""
    # Arrange
    service = RoomService(json_db)
    service.add("room a", 50)
    
    # Act
    response = service.edit("non-existent", "new name", 100)
    
    # Assert
    assert response.error == ERROR_ELEMENT_NOT_FOUND


# ========== TEST: REMOVE ROOM ==========
def test_remove_room_deletes_from_database(json_db: Path):
    """Test that removing a room deletes it from database."""
    # Arrange
    service = RoomService(json_db)
    service.add("room to delete", 50)
    
    # Act
    response = service.remove("Room to delete.")
    
    # Assert
    assert response.error == SUCCESS
    assert len(service._db_handler.read("rooms").list) == 0


def test_remove_room_not_found(json_db: Path):
    """Test removing a non-existing room."""
    # Arrange
    service = RoomService(json_db)
    service.add("room a", 50)
    
    # Act
    response = service.remove("non-existent")
    
    # Assert
    # This will raise an IndexError because remove_index is -1
    # The current implementation has a bug - it should check before pop


def test_remove_specific_room_from_multiple(json_db: Path):
    """Test removing one room when multiple exist."""
    # Arrange
    service = RoomService(json_db)
    service.add("room a", 50)
    service.add("room b", 100)
    service.add("room c", 75)
    
    # Act
    service.remove("Room b.")
    
    # Assert
    remaining = service._db_handler.read("rooms").list
    assert len(remaining) == 2
    names = [r["name"] for r in remaining]
    assert "Room b." not in names


# ========== TEST: ROOM OBJECT ==========
def test_room_to_dict(json_db: Path):
    """Test Room.to_dict() conversion."""
    # Arrange
    room = Room(
        id="test-123",
        name="Test Room",
        capacity=50
    )
    
    # Act
    result = room.to_dict()
    
    # Assert
    assert result["id"] == "test-123"
    assert result["name"] == "Test Room"
    assert result["capacity"] == 50


def test_room_dataclass_properties():
    """Test Room dataclass properties."""
    # Arrange & Act
    room = Room(
        id="uuid-456",
        name="Sample Room",
        capacity=100
    )
    
    # Assert
    assert room.id == "uuid-456"
    assert room.name == "Sample Room"
    assert room.capacity == 100


# ========== TEST: ROOM SERVICE RESPONSE ==========
def test_room_service_response_success():
    """Test RoomServiceResponse with success."""
    # Arrange & Act
    response = RoomServiceResponse(
        list=[],
        error=SUCCESS
    )
    
    # Assert
    assert response.error == SUCCESS
    assert response.list == []


def test_room_service_response_error():
    """Test RoomServiceResponse with error."""
    # Arrange & Act
    response = RoomServiceResponse(
        list=[],
        error=ERROR_ELEMENT_NOT_FOUND
    )
    
    # Assert
    assert response.error == ERROR_ELEMENT_NOT_FOUND


# ========== FIXTURES ==========
@pytest.fixture
def json_db(tmp_path: Path):
    """
    Creates an empty book.json file and returns its path.
    """
    db_file = tmp_path / "book.json"

    with open(db_file, "w") as f:
        json.dump({"rooms": [], "bookings": []}, f, indent=4)

    return db_file