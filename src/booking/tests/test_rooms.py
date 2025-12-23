import json
import pytest

from booking.models import book
from typing import Any

import pytest
from typing import Any

ROOM_CASES = [
    {"name": "the great salon.", "capacity": 250},
    {"name": "macacha güemes.", "capacity": 50},
]


@pytest.mark.parametrize("room", ROOM_CASES)
def test_add_room_persists_room(json_db, room: dict[str, Any]):
    # Arrange
    service = book.RoomService(json_db)

    # Act
    service.add(room["name"], room["capacity"])

    # Assert
    room_list = service._db_handler.read("rooms").list

    assert len(room_list) == 1
    assert room_list[0]["name"] == room["name"]
    assert room_list[0]["capacity"] == room["capacity"]


# ---------- Fixtures ----------
@pytest.fixture
def json_db(tmp_path: book.Path):
    """
    Creates an empty book.json file and returns its path.
    """
    db_file = tmp_path / "book.json"

    with open(db_file, "w") as f:
        json.dump({"rooms": []}, f, indent=4)

    return db_file