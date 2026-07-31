from flask import Flask, jsonify, request
import mysql.connector
import os

app = Flask(__name__, static_folder='static', static_url_path='')

# Update Password to your own mysql password
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Alisha'  # UPDATE
MYSQL_DATABASE = 'task_manager_db'

# Establish db connection
def get_db_connection(init=False):
    if init:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=3306
        )
    else:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=3306
        )

# Create db and tables if they do not exist
def init_db():
    try:
        # Connect without specifying db to create it
        conn = get_db_connection(init=True)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.close()
        conn.close()

        # Connect with db to create the table
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'tasks'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check columns to ensure 'description' exists
            cursor.execute("SHOW COLUMNS FROM tasks")
            cols = [row[0] for row in cursor.fetchall()]
            if 'description' not in cols:
                if 'employee_name' in cols:
                    print("Old 'tasks' table from previous run detected. Recreating table...")
                    cursor.execute("DROP TABLE tasks")
                    cursor.execute("""
                        CREATE TABLE tasks (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            completed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                        )
                    """)
                else:
                    print("Altering table 'tasks' to add 'description' column...")
                    cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT AFTER title")
        else:
            # Create fresh table
            cursor.execute("""
                CREATE TABLE tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
        conn.commit()
        cursor.close()
        conn.close()
        print("MySQL database and tables checked/initialized successfully.")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Please check your MySQL service and connection credentials in app.py.")

# Runs index.html
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, title, description, completed, created_at FROM tasks ORDER BY id DESC")
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert completed to boolean for Javascript ease
        for task in tasks:
            task['completed'] = bool(task['completed'])
            task['created_at'] = str(task['created_at'])
            if task['description'] is None:
                task['description'] = ''
            
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({
            "error": "Database Connection Failed",
            "message": str(e),
            "hint": "Please verify that MySQL is running and your connection settings in app.py are correct."
        }), 500

# Add a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json or {}
    title = data.get('title')
    description = data.get('description', '')
    completed = data.get('completed', False)

    if not title:
        return jsonify({"error": "Missing Required Fields", "message": "Task title is required."}), 400

    completed_val = 1 if completed else 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, completed) VALUES (%s, %s, %s)",
            (title, description, completed_val)
        )
        conn.commit()
        task_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Task created successfully", "id": task_id}), 201
    except Exception as e:
        return jsonify({"error": "Database Query Failed", "message": str(e)}), 500

# Update existing task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json or {}
    title = data.get('title')
    description = data.get('description', '')
    completed = data.get('completed')

    if not title or completed is None:
        return jsonify({"error": "Missing Required Fields", "message": "Task title and completed status are required."}), 400

    completed_val = 1 if completed else 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title = %s, description = %s, completed = %s WHERE id = %s",
            (title, description, completed_val, task_id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"error": "Not Found", "message": f"Task with ID {task_id} not found."}), 404

        return jsonify({"success": True, "message": "Task updated successfully", "id": task_id}), 200
    except Exception as e:
        return jsonify({"error": "Database Query Failed", "message": str(e)}), 500

# Delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"error": "Not Found", "message": f"Task with ID {task_id} not found."}), 404

        return jsonify({"success": True, "message": "Task deleted successfully", "id": task_id}), 200
    except Exception as e:
        return jsonify({"error": "Database Query Failed", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize db
    init_db()
    
    # Run server
    print("Starting Task Manager web application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
