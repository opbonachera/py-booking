import typer
from pathlib import Path
from typing import Optional
from booking import ERRORS, __app_name__, __version__, config, database, DB_INIT_ERROR, DEFAULT
from booking.models.room import RoomService
from booking.models.book import BookingService
from booking.validators import BookingValidator, DateValidator
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


@app.command()
def book(
    room_name: str = typer.Option(..., "--room-name", "-r", help="Name of the room to book"),
    start_date: str = typer.Option(..., "--start-date", "-s", help="Check-in date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., "--end-date", "-e", help="Check-out date (YYYY-MM-DD)"),
) -> None:
    """Book a room for specific dates."""
    db_path = config._get_database_path()
    room_service = RoomService(db_path=db_path)
    booking_service = BookingService(db_path=db_path)
    
    # Validate dates format and values
    is_valid, error_msg = BookingValidator.validate_booking_dates(start_date, end_date)
    if not is_valid:
        typer.secho(f"Date validation error: {error_msg}", fg=typer.colors.RED)
        return
    
    # Check if room exists
    room_response = room_service.get_room_by_name(room_name)
    if room_response.error:
        typer.secho(f"Room '{room_name}' not found in database", fg=typer.colors.RED)
        return
    
    room = room_response.list[0]
    room_id = room.get("id")
    
    # Check for booking conflicts
    existing_bookings_response = booking_service.get_bookings_by_room(room_id)
    existing_bookings = existing_bookings_response.list if existing_bookings_response.error == 0 else []
    
    is_available, conflict_msg = BookingValidator.check_room_availability(
        room_id, start_date, end_date, existing_bookings
    )
    
    if not is_available:
        typer.secho(f"Booking failed: {conflict_msg}", fg=typer.colors.RED)
        return
    
    # Create the booking
    booking_response = booking_service.add(room_name, room_id, start_date, end_date)
    
    if booking_response.error:
        typer.secho(f"Booking failed with error code {booking_response.error}", fg=typer.colors.RED)
        return
    
    booking = booking_response.booking
    typer.secho(
        f"✓ Room '{room_name}' successfully booked from {start_date} to {end_date}\n"
        f"  Booking ID: {booking.id}",
        fg=typer.colors.GREEN
    )


@app.command()
def list_bookings(
    room_name: str = typer.Option(None, "--room-name", "-r", help="Filter bookings by room name (optional)"),
) -> None:
    """List all bookings or bookings for a specific room."""
    db_path = config._get_database_path()
    booking_service = BookingService(db_path=db_path)
    room_service = RoomService(db_path=db_path)
    
    bookings_response = booking_service.get_bookings()
    
    if bookings_response.error:
        typer.secho("Failed to retrieve bookings", fg=typer.colors.RED)
        return
    
    bookings = bookings_response.list
    
    # Filter by room name if provided
    if room_name:
        bookings = [b for b in bookings if b.room_name.lower() == room_name.lower()]
        if not bookings:
            typer.secho(f"No bookings found for room '{room_name}'", fg=typer.colors.YELLOW)
            return
    
    if not bookings:
        typer.secho("No bookings found", fg=typer.colors.YELLOW)
        return
    
    # Display bookings
    typer.secho("\n" + "="*70, fg=typer.colors.CYAN)
    typer.secho("BOOKINGS", fg=typer.colors.CYAN)
    typer.secho("="*70, fg=typer.colors.CYAN)
    
    for booking in bookings:
        typer.secho(
            f"Room: {booking.room_name}\n"
            f"  Check-in:  {booking.start_date}\n"
            f"  Check-out: {booking.end_date}\n"
            f"  Booking ID: {booking.id}\n",
            fg=typer.colors.GREEN
        )