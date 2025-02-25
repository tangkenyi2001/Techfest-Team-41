# Backend
## Prerequisites
uv is installed
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
## Setup
To set up venv
```
uv venv
```
To activate venv
```
.venv/Scripts/activate
```

## Installation of all packages
To install all the packages in the `pyproject.toml` file, run the following cmd:
```
uv sync
```

## To add new packages
```
uv add <package-name>
```

## How to run backend
``` bash
cd techfest
uvicorn main:app --reload
```