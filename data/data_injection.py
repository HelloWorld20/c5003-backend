import mysql.connector
from mysql.connector import errorcode
import os

# --- 1. DATABASE CONFIGURATION ---
DB_CONFIG = {
    'user': 'root',
    'password': 'ss65492367', # <-- IMPORTANT: SET YOUR PASSWORD
    'host': '127.0.0.1',
    'raise_on_warnings': False, # This is crucial for the splitting method
}
DB_NAME = 'employees'

# --- 2. LIST OF ALL SQL/DUMP FILES IN THE CORRECT ORDER ---
SQL_FILES_TO_LOAD = [
    'employees.sql',
    'load_departments.dump',
    'load_employees.dump',
    'load_dept_emp.dump',
    'load_dept_manager.dump',
    'load_titles.dump',
    'load_salaries1.dump',
    'load_salaries2.dump',
    'load_salaries3.dump',
    'show_elapsed.sql'
]

def main():
    """
    Connects to MySQL and executes all required SQL files by splitting them
    into individual statements and consuming any results produced along the way.
    """
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        script_dir = os.getcwd()

    full_sql_script = ""
    print("Reading and combining all SQL files...")

    for filename in SQL_FILES_TO_LOAD:
        file_path = os.path.join(script_dir, filename)
        if not os.path.exists(file_path):
            print(f"FATAL ERROR: Required file not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().replace('\r\n', '\n')
            lines = [line for line in content.split('\n') if not line.strip().lower().startswith('source ')]
            full_sql_script += "\n".join(lines)
    
    print("All files loaded and combined.")
    
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("Executing combined SQL script... This will take several minutes.")

        sql_statements = full_sql_script.split(';')

        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement)
                if cursor.with_rows:
                    cursor.fetchall() # Fetch and discard rows to clear the buffer

        connection.commit()
        print("\nAll scripts executed successfully! The 'employees' database is now populated.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Authentication Error: Please check your MySQL username and password.")
        else:
            print(f"A MySQL error occurred: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == '__main__':
    main()