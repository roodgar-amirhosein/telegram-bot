# Telegram Bot Project

This project is a Telegram bot integrated with OpenAI and connected to a PostgreSQL database using Docker for easy setup and deployment.

## Prerequisites

Before starting, make sure you have the following installed on your system:

- **Python 3.10+**
- **Docker**
- **Docker Compose**

## Setup Instructions

1. **Create a Virtual Environment**

   First, create a virtual environment in the root directory of the project:

   ```bash
   python3 -m venv venv
   ```

2. **Install Dependencies**

   Install the required Python dependencies using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```
   

3. **Environment Variables Setup**


- There is a .sample-env file that contains the format for the .env file.
- You should create a .env file and set values for the required variables before proceeding.


4. **Docker Setup**

   Ensure that Docker and Docker Compose are installed on your system.

   - If you haven't installed Docker, you can follow the official installation guide: [Docker Installation](https://docs.docker.com/get-docker/)
   - For Docker Compose, follow the guide here: [Docker Compose Installation](https://docs.docker.com/compose/install/)

5. **Start the Services**

   Run the following command to start the database service in the background using Docker Compose:

   ```bash
   docker-compose up -d
   ```

   This will pull the required Docker images and start the PostgreSQL database container.

6. **Running the Bot**

   After the database is up and running, execute the `telegram-bot.py` file to start the bot:

   ```bash
   python manage.py migrate
   python telegram_bot.py
   ```

   Your Telegram bot should now be running.

## Important Note

- The server must have access to a VPN in order to connect to Telegram's API.
- Make sure the `.env` file is correctly configured .

---

Enjoy using the bot! Feel free to reach out if you have any questions.
