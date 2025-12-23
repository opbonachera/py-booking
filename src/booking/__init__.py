""" Top-level package for Booking. """

__app_name__ = "booking"
__version__ = "0.1.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    DB_INIT_ERROR,
    JSON_ERROR,
    ID_ERROR,
    DUPLICATED_ROOM_NAME, 
    ERROR_ELEMENT_NOT_FOUND,
    DEFAULT
) = range(11)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "to-do id error",
    ERROR_ELEMENT_NOT_FOUND: "element to edit was not found",
    DUPLICATED_ROOM_NAME: "a room with the same name already exists",
    DB_INIT_ERROR: "error initializing database in specified path. using default",
    DEFAULT:"",
}