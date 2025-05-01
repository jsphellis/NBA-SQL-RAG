import os
import subprocess
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.AppUtils.Config import DB_CONFIG

def export_database_to_sql():
    """
    Exports the NBA database to a SQL file using mysqldump
    """
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nba_database_{timestamp}.sql"
    filepath = os.path.join(export_dir, filename)
    
    mysqldump_cmd = [
        'mysqldump',
        f'--host={DB_CONFIG["host"]}',
        f'--user={DB_CONFIG["user"]}',
        f'--port={DB_CONFIG["port"]}',
        f'--password={DB_CONFIG["password"]}',
        DB_CONFIG["database"],
        '--result-file=' + filepath
    ]
    
    try:
        print(f"Exporting database {DB_CONFIG['database']} to {filepath}...")
        subprocess.run(mysqldump_cmd, check=True)
        print(f"Database exported successfully to {filepath}")
        return filepath
    except subprocess.CalledProcessError as e:
        print(f"Error exporting database: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    export_path = export_database_to_sql()
    if export_path:
        print(f"You can now import this file into another MySQL database using:")
        print(f"mysql -u [username] -p [database_name] < {export_path}") 