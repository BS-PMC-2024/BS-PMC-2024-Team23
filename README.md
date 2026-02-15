# FitAI(Python, Flask, PostgresSQL(Docker), HTML, CSS)

FitAI is a personalized fitness and health management platform that leverages AI to provide tailored workout plans, diet suggestions, and progress tracking.

# Technologies:
- **Backend:** Python, Flask (REST API)
- **Database:** PostgresSQL(SQLAlchemy ORM) Container(Docker)
- **AI Integration:** OPEN AI 
- **Frontend:** HTML, CSS, React (optional for feuture iterations)
  
<img width="1919" height="1079" alt="1" src="https://github.com/user-attachments/assets/ee84fbef-e29d-4d25-a613-e54a1d911d8e" />
<img width="1919" height="1079" alt="4" src="https://github.com/user-attachments/assets/9a3c0ea7-2945-4eac-985e-b2654481208d" />

# Features
- **User authentication:** Users can register and log in to the platform.
- **CRUD operations:** Create, Read, Update, and Delete operations.
- **Set Fitness Goals**: Users can set their fitness goals, fitness level, and training frequency.
- **AI-Generated Programs**: The system provides AI-generated workout programs and diet suggestions.
- **Progress Tracking**: Users can track their progress, update their training details, and view AI-generated suggestions for improvement.
- **Expected Results**: Users can view their expected progress over a selected timeframe.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Docker and DBeaver Setup](#docker-and-dbeaver-setup)

## Installation

To install and run the project locally, follow these steps:

### Prerequisites
- Python 3.7+
- Docker
- DBeaver
- Internet Browser

### Steps
1. Clone the repository.
2. Install the required Python packages:
    ```bash
    pip install flask flask_sqlalchemy flask_migrate openai psycopg2-binary python-dotenv
    ```
3. Run `main.py` to start the Flask server:
    ```bash
    python main.py
    ```
4. Access the website by clicking the link provided in the terminal or navigating to `http://127.0.0.1:5001/` in your browser.

## Docker and DBeaver Setup

### Docker
- **Image**: `postgres:latest`
- **Container Name**: `postgres-container`
- **Environment**:
  - `POSTGRES_USER`: myuser
  - `POSTGRES_PASSWORD`: mypassword
  - `POSTGRES_DB`: mydatabase
- **Port**: `5432`

### DBeaver
- **Port**: `5432`

## Usage

### Access the Website
- Open your browser and navigate to `http://127.0.0.1:5001/`.

## Project Structure

- `main.py`: The main entry point of the application.
- `templates/`: Contains HTML templates.
- `static/`: Contains static files like CSS and JavaScript.
- `openAIManager.py`: Handles all OpenAI API interactions.

## Dependencies

The project requires the following Python packages:

- `flask`
- `flask_sqlalchemy`
- `flask_migrate`
- `openai`
- `psycopg2-binary`
- `python-dotenv`

To install these dependencies, use the following command:

```bash
pip install flask flask_sqlalchemy flask_migrate openai psycopg2-binary python-dotenv
```

## Docker and DBeaver Setup

### Docker
1. **Start a PostgreSQL container:**
    ```bash
    docker run --name postgres-container -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mydatabase -p 5432:5432 -d postgres:latest
    ```
Or manually through the software's UI

### DBeaver
1. **Connect to the PostgreSQL container:**
   - Open DBeaver.
   - Create a new connection.
   - Set the hostname to `localhost` and the port to `5432`.
   - Use the credentials:
     - User: `myuser`
     - Password: `mypassword`
     - Database: `mydatabase`






