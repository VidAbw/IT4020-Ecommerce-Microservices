import sqlite3
import os
import sys

def display_sqlite_data():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change current working directory to the script's directory
    os.chdir(script_dir)
    
    # Find all .db files in the current directory
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    
    if not db_files:
        print(f"No .db files found in the directory: {script_dir}")
        print("Note: The database file is created when the microservice is first run.")
        return

    # Use the first .db file found
    db_path = db_files[0]
    print(f"Reading database: {db_path} in {script_dir}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return

        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            # Skip sqlite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"\n--- Data from Table: {table_name} ---")
            
            # Fetch table column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Fetch table data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print("No data found in this table.")
            else:
                # Print column headers
                header = " | ".join(columns)
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in rows:
                    print(" | ".join(map(str, row)))
                    
        conn.close()
    except sqlite3.Error as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    display_sqlite_data()
