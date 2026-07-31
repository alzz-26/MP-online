# Task Manager with Live Database

A Task Manager dashboard featuring a responsive UI, real-time database, and complete CRUD operations. Built with HTML, CSS, JavaScript, Python (Flask), and MySQL.

## Prerequisites

1. **Python 3**: Make sure you have Python installed. You can check with:
   ```bash
   python --version
   ```
2. **MySQL Server**: Ensure your local MySQL instance is running.
3. **Libraries**: Install the required Python packages:
   ```bash
   pip install flask mysql-connector-python
   ```

## Configuration

1. Open `app.py`.
2. Locate the **DATABASE CONFIGURATION** block at the top:
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'your_mysql_password'  # Replace with your MySQL password
   MYSQL_DATABASE = 'task_manager_db'
   ```
3. Update `MYSQL_PASSWORD` (and `MYSQL_USER`/`MYSQL_HOST` if different) to match your local MySQL configuration.

*Note: The application is designed to automatically create the database (`task_manager_db`) and table (`tasks`) if they do not exist, so you do not need to import any SQL file manually!*

## Running the Application

1. Open a terminal/command prompt in this project folder.
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. You will see output indicating the server is running, for example:
   `Starting Task Manager web application on http://127.0.0.1:5000`
4. Open your web browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Project Structure

- `app.py`: Flask backend serving JSON API endpoints and static assets.
- `schema.sql`: SQL database schema backup file.
- `static/`:
  - `index.html`: The HTML layout.
  - `style.css`: Page styling.
  - `app.js`: Frontend logic, event handling, AJAX CRUD requests, and live database synchronization.
