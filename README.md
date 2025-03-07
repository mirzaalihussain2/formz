# Running backend

## Setup
1. Check you have Python 3.11 installed, a specific version number should be returned in the Terminal (e.g. `Python 3.11.11`).
    ```bash
    python3.11 --version
    ```
<br>

2. Navigate to `backend` folder and create an `.env.local` file (copying `.env.example`).
    ```bash
    cd backend && cp .env.example .env.local
    ```
<br>

## Running backend locally
The backend can be run:
* within a virtual environment or a docker container
* in development or production mode

<br>

From the backend folder, there are 4 ways to run the backend:
| **environment** | **mode** | **command** |
|-----------------|----------|-------------|
| virtual env | dev | `./boot.sh venv dev` |
| virtual env | prod | `./boot.sh venv prod` |
| docker | dev | `./boot.sh docker dev` |
| docker | prod | `./boot.sh docker prod` |  

Backend served at [http://localhost:8080](http://localhost:8080) - only route available is 'Hello, World!' smoke test on index route (`/`).
