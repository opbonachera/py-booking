
# Booking App

This application allows an user to create, edit and remove rooms. They can also book their assistence to them. 


## Features

- Add, edit and remove rooms
- Unit testing
- CLI application
- Cross platform

## Running Tests

To run tests, run the following command

```bash
  uv run pytest -m [module-name]
```

## Initialize and run project

Clone this project from Github.
Open your CMD, place yourself in your project directory and then run

```bash
   uv run -m booking init
```

## Commands

### Add room 

```bash
   uv run -m booking add --name=[Room name, str] --capacity=[Room capacity, int]
```

### List rooms
```bashs
   uv run -m booking get --limit=[Maximum number of rooms to get, int]
```


## Tech Stack

- Python
- Typer
- Annotations
- Pytest

