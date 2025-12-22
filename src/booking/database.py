import configparser
import json
from typing import Any, Dict, List, NamedTuple
from pathlib import Path
from booking import DB_WRITE_ERROR, DB_READ_ERROR, JSON_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH  = Path.home().joinpath(
    "." + Path.home().stem + "_bookings.json"
)

class DBResponse(NamedTuple):
    list: List[Dict[str, Any]]
    code: int


class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        
    def get_path(self, db_path: Path) -> Path:
        self._db_path = db_path
    
    def read(self, key: str) -> DBResponse:
        try:
            with self._db_path.open("r") as db:
                data = json.load(db).get(key, [])
                
                if data:
                    return DBResponse(data, SUCCESS)
                else:
                    return DBResponse([], JSON_ERROR)
                
        except OSError:
            return DBResponse([], DB_READ_ERROR)
    
    def write(self, key: str, value: list[Any]) -> DBResponse:
        try:
            data = {}
            if self._db_path.exists():
                with self._db_path.open("r") as db:
                    try:
                        data = json.load(db)
                    except json.JSONDecodeError:
                        data = {}

            data[key] = value

            with self._db_path.open("w") as db:
                json.dump(data, db, indent=4)

            return DBResponse(data[key], SUCCESS)

        except OSError:
            return DBResponse([], DB_WRITE_ERROR)