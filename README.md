# BS-PMC-2024-Team23 Project

## Introduction
This project is a Flask web application designed for fitness tracking and AI-generated suggestions based on user data.

## Prerequisites
1. **Python**: Ensure Python 3.7 or above is installed. You can download it from [python.org](https://www.python.org/downloads/).
2. **Pip**: Make sure `pip` (Python package installer) is installed.
3. **Docker (Optional)**: If you prefer running the application in a containerized environment, install Docker from [docker.com](https://www.docker.com/get-started).
4. **Git**: For version control, ensure that Git is installed on your system.

## Installation Instructions

### Step 1: Clone the Repository
Clone the repository from GitHub:
```bash



cd BS-PMC-2024-Team23


### Step 2: Set up a Virtual Environment
**python -m venv venv**
source venv/bin/activate   # On Windows use `venv\Scripts\activate`

#### Step 3: Install Required Packages
Install the required Python packages using pip:

pip install -r requirements.txt

### Step 4: Configure Environment Variables
Create a .env file in the project root directory and set the necessary environment variables, such as:

FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///users.sqlite3

