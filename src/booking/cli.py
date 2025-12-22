import typer
from booking import models
from pathlib import Path
from typing import Optional
from booking import ERRORS, __app_name__, __version__, config, database

app = typer.Typer()
db = database.DatabaseHandler(database.DEFAULT_DB_FILE_PATH)

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
        prompt="enter database location"
    )
)-> None:
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}',
            fg=typer.colors.RED
        )   
        raise typer.Exit(1)
    
    db_init_error = db.init(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The to-do database is {db_path}", fg=typer.colors.GREEN)

@app.command()
def add(
    name: str = typer.Option(..., "--name", "-n", help="The room name."),
    capacity: int = typer.Option(..., "--capacity", "-c", help="The room capacity."),
)->None:
    room_service = models.RoomService(db_path=Path(database.DEFAULT_DB_FILE_PATH))
    room = room_service.add(name, capacity)

    read_rooms = room_service.get_rooms()
    
    if read_rooms.error:
        typer.secho(f"Reading rooms failed with {read_rooms.error}", fg=typer.colors.RED)
    else:
        typer.secho(f"Rooms: {read_rooms.list}", fg=typer.colors.GREEN)

    if room.error:
        typer.secho(f"Adding room failed with {room.error}", fg=typer.colors.RED)
    
    typer.secho(f"Room added: {room.data}", fg=typer.colors.GREEN)

@app.command()
def get(
    limit: int = typer.Option(None, "--limit", "-l", help="Maximum number of rooms to get"),
)->None:
    room_service = models.RoomService(db_path=Path(database.DEFAULT_DB_FILE_PATH))
    
    room_list = room_service.get_rooms()
    
    typer.secho(f"{room_list.list[:limit]}", fg=typer.colors.GREEN)