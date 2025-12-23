import uuid
from dataclasses import dataclass
from booking import database
from pathlib import Path
from booking import ERRORS, SUCCESS, ERROR_ELEMENT_NOT_FOUND, DUPLICATED_ROOM_NAME

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
        self._db_handler = database.DatabaseHandler(db_path)
    
    def get_rooms(self) -> list[Room]:
        read = self._db_handler.read("rooms")
        
        if read.code:
            return RoomServiceResponse([], ERRORS[read.code])
        
        rooms_data = [
            {"name": room.get("name", ""), "capacity": room.get("capacity", "")} 
            for room in read.list
        ]
        
        return RoomServiceResponse(rooms_data, SUCCESS)
        
    def add(self, name: str, capacity: int)->Room:
        name += ('.' if not name.endswith('.') else '').capitalize()
        capacity = capacity if capacity > -1 else 'not informed'
        
        room = Room(
            uuid.uuid4(),
            name,
            capacity
        )
        
        room_list = self._db_handler.read("rooms").list
        
        index_item = next((i for i, room in enumerate(room_list) if room["name"].lower() == name.lower()), -1)

        if index_item > -1:
            return RoomServiceResponse(room, DUPLICATED_ROOM_NAME)
            
        room_list.append(room.to_dict())
        
        self._db_handler.write("rooms", room_list)
        
        return RoomServiceResponse(room, SUCCESS)
    
    def edit(self, room_name: str, new_name: str, capacity: int)->Room:
        room_list = self._db_handler.read("rooms").list
        
        index_item_to_edit = next((i for i, room in enumerate(room_list) if room["name"] == room_name), -1)
        if index_item_to_edit == -1:
            return RoomServiceResponse([], ERROR_ELEMENT_NOT_FOUND)
        
        edited_element = {
            "id": room_list[index_item_to_edit].id,
            "name": new_name if new_name else room_list[index_item_to_edit].name,
            "capacity": capacity if capacity else room_list[index_item_to_edit].capacity
        } 
        
        room_list[index_item_to_edit] = edited_element

        self._db_handler.write("rooms", room_list)
        
        return RoomServiceResponse(room_list[index_item_to_edit], SUCCESS)
    
    def remove(self, room_name:str)->RoomServiceResponse:
        room_list = self._db_handler.read("rooms").list
        
        remove_index = next((i for i, room in enumerate(room_list) if room["name"] == room_name), -1)
        removed_element = room_list[remove_index]
        
        if remove_index < 0:
            return RoomServiceResponse([], ERROR_ELEMENT_NOT_FOUND)
        
        room_list.pop(remove_index)
        
        self._db_handler.write("rooms", room_list)
        
        return RoomServiceResponse(removed_element, SUCCESS)