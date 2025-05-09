"""
sql_dump.py

This file contains the functions for exporting the NBA database to a SQL file
"""

import os
import sys
import subprocess
from datetime import datetime
from src.utils.config import DB_CONFIG

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

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
        print(f"Error executing mysqldump command: {e}")
        return None
    except FileNotFoundError as e:
        print(f"mysqldump command not found. Please ensure MySQL client tools are installed: {e}")
        return None
    except PermissionError as e:
        print(f"Permission denied when executing mysqldump: {e}")
        return None
    except OSError as e:
        print(f"Operating system error while executing mysqldump: {e}")
        return None

if __name__ == "__main__":
    export_database_to_sql()
