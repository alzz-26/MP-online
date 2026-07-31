import mysql.connector
import sys
import os

# Fixed MySQL configurations
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Alisha'
MYSQL_DATABASE = 'library_manager_db'

def get_db_connection(init=False):
    """Establishes connection to MySQL database using fixed credentials."""
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

def init_db():
    """Reads schema.sql and initializes the database and tables."""
    print("Initializing database from schema.sql...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, 'schema.sql')
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    # Connect to MySQL server and execute creation commands
    conn = get_db_connection(init=True)
    cursor = conn.cursor()
    
    commands = sql_script.split(';')
    for command in commands:
        command = command.strip()
        if command:
            cursor.execute(command)
        
    conn.commit()
    cursor.close()
    conn.close()
    print("Database and tables initialized successfully.")

# Helper function to print tables in CLI
def print_table(headers, rows):
    if not rows:
        print("\n--- No Records Found ---")
        return
        
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
            
    fmt = " | ".join([f"{{:<{w}}}" for w in widths])
    border = "-+-".join(["-" * w for w in widths])
    
    print("\n" + border)
    print(fmt.format(*headers))
    print(border)
    for row in rows:
        print(fmt.format(*[str(val) for val in row]))
    print(border + "\n")

# --- Books operations ---
def add_book():
    print("\n--- Add New Book ---")
    name = input("Enter book name: ")
    author = input("Enter author: ")
    tot_copies = int(input("Enter total copies: "))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Books (book_name, author, tot_copies, remaining_copies) VALUES (%s, %s, %s, %s)",
        (name, author, tot_copies, tot_copies)
    )
    conn.commit()
    print(f"Book added successfully (Book ID: {cursor.lastrowid}).")
    cursor.close()
    conn.close()

def view_books():
    print("\n--- Books List ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Book_id, book_name, author, tot_copies, remaining_copies FROM Books")
    rows = cursor.fetchall()
    print_table(["Book ID", "Book Name", "Author", "Total Copies", "Remaining Copies"], rows)
    cursor.close()
    conn.close()

# --- Customer operations ---
def add_customer():
    print("\n--- Add New Customer ---")
    name = input("Enter customer name: ")
    fees = float(input("Enter initial fees paid (or 0): ") or 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Customer (cust_name, issued_books, Fees_paid) VALUES (%s, %s, %s)",
        (name, 0, fees)
    )
    conn.commit()
    print(f"Customer registered successfully (Customer ID: {cursor.lastrowid}).")
    cursor.close()
    conn.close()

def view_customers():
    print("\n--- Customer List ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cust_id, cust_name, issued_books, Fees_paid FROM Customer")
    rows = cursor.fetchall()
    print_table(["Customer ID", "Customer Name", "Issued Books Count", "Fees Paid"], rows)
    cursor.close()
    conn.close()

def pay_fees():
    print("\n--- Pay Outstanding Fees ---")
    cust_id = int(input("Enter Customer ID: "))
    amount = float(input("Enter amount to pay: "))

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current fees
    cursor.execute("SELECT Fees_paid FROM Customer WHERE cust_id = %s", (cust_id,))
    current_fees = cursor.fetchone()[0]
    
    # Update fees
    new_fees = float(current_fees) + amount
    cursor.execute("UPDATE Customer SET Fees_paid = %s WHERE cust_id = %s", (new_fees, cust_id))
    conn.commit()
    print(f"Payment successful. New total fees paid: {new_fees}")
    cursor.close()
    conn.close()

# --- Issue & Return operations ---
def issue_book():
    print("\n--- Issue a Book ---")
    cust_id = int(input("Enter Customer ID: "))
    book_id = int(input("Enter Book ID: "))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get remaining copies
    cursor.execute("SELECT remaining_copies FROM Books WHERE Book_id = %s", (book_id,))
    remaining = cursor.fetchone()[0]

    if remaining > 0:
        # Decrement remaining copies
        cursor.execute("UPDATE Books SET remaining_copies = remaining_copies - 1 WHERE Book_id = %s", (book_id,))
        # Increment customer's issued count
        cursor.execute("UPDATE Customer SET issued_books = issued_books + 1 WHERE cust_id = %s", (cust_id,))
        conn.commit()
        print("Book issued successfully.")
    else:
        print("Error: No copies available.")
        
    cursor.close()
    conn.close()

def return_book():
    print("\n--- Return a Book ---")
    cust_id = int(input("Enter Customer ID: "))
    book_id = int(input("Enter Book ID: "))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get customer's issued count
    cursor.execute("SELECT issued_books FROM Customer WHERE cust_id = %s", (cust_id,))
    issued_count = cursor.fetchone()[0]

    if issued_count > 0:
        # Increment remaining copies
        cursor.execute("UPDATE Books SET remaining_copies = remaining_copies + 1 WHERE Book_id = %s", (book_id,))
        # Decrement customer's issued count
        cursor.execute("UPDATE Customer SET issued_books = issued_books - 1 WHERE cust_id = %s", (cust_id,))
        conn.commit()
        print("Book returned successfully.")
    else:
        print("Error: Customer does not have any books issued.")
        
    cursor.close()
    conn.close()

# --- Menu ---
def main_menu():
    init_db()
    
    while True:
        print("\n" + "=" * 80)
        print("                        LIBRARY MANAGEMENT SYSTEM")
        print("=" * 80)
        print("  Prepared by -> Alisha Basa - IN26011102 - Batch 9A")
        print("  Software Engineering and Development Internship")
        print("-" * 80)
        print("  1. Add Book")
        print("  2. View All Books")
        print("  3. Add Customer")
        print("  4. View All Customers")
        print("  5. Issue Book")
        print("  6. Return Book")
        print("  7. Pay Outstanding Fees")
        print("  8. Exit")
        print("=" * 80)
        
        choice = input("Enter choice (1-8): ").strip()
        
        if choice == '1':
            add_book()
        elif choice == '2':
            view_books()
        elif choice == '3':
            add_customer()
        elif choice == '4':
            view_customers()
        elif choice == '5':
            issue_book()
        elif choice == '6':
            return_book()
        elif choice == '7':
            pay_fees()
        elif choice == '8':
            print("\nExiting. Goodbye!\n")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
