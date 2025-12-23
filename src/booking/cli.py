import typer
from pathlib import Path
from typing import Optional
from booking import ERRORS, __app_name__, __version__, config, database, DB_INIT_ERROR, DEFAULT
from booking.models.room import RoomService
from configparser import ConfigParser

app = typer.Typer()

def _version_callback(value: bool)->None:
    if value:
        typer.echo(f'{__app_name__} v{__version__}')
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="to-do database location?",
    ),
) -> None:
    """Initialize the to-do database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[DEFAULT]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    database.DatabaseHandler(Path(db_path))
    
    
    typer.secho(f"App correctly initialized. DB: {db_path}", fg=typer.colors.GREEN)

@app.command()
def add(
    name: str = typer.Option(..., "--name", "-n", help="The room name."),
    capacity: int = typer.Option(..., "--capacity", "-c", help="The room capacity."),
)->None:
    room_service = RoomService(db_path=config._get_database_path())
    room = room_service.add(name, capacity)

    if room.error:
        typer.secho(f"Adding new room failed, {ERRORS[room.error]}", fg=typer.colors.RED)
        return 

    read_rooms = room_service.get_rooms()
    
    if read_rooms.error:
        typer.secho(f"Reading rooms failed with {read_rooms.error}", fg=typer.colors.RED)
    else:
        typer.secho(f"Rooms: {read_rooms.list}", fg=typer.colors.GREEN)
    
    typer.secho(f"Room added: {room.list}", fg=typer.colors.GREEN)

@app.command()
def get(
    limit: int = typer.Option(None, "--limit", "-l", help="Maximum number of rooms to get"),
)->None:
    room_service = RoomService(db_path=config._get_database_path)
    
    room_list = room_service.get_rooms()
    
    typer.secho(f"{room_list.list[:limit]}", fg=typer.colors.GREEN)

@app.command()
def edit(
    room_name: str = typer.Option(..., "--room-name", "-rn", help="Name of room to edit"),
    new_room_name: str = typer.Option(None, "--new-room-name", "-nn", help="New name of the room"),
    new_capacity: int = typer.Option(None, "--new-capacity", "-nc", help="New name of the room")
)->None:
    room_service = RoomService(db_path=Path(database.DEFAULT_DB_FILE_PATH))
    
    edited_room = room_service.edit(room_name, new_room_name, new_capacity)
    
    typer.secho(f"{edited_room}", fg=typer.colors.GREEN)