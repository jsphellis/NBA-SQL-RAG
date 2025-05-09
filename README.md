# 🏀 ChatDB - NBA

Natural language interface for exploring NBA database.

## 📁 Project Structure

### 🛠️ Data Folders

- **/data** - Includes csv files from data scraping (box_score, players, data)
- **/SQL_Data** - Includes exported SQL data from interface use

### 🛠️ Source Code

#### `src/DataUtils/`
- **NBA_Data_Scrape.py** - Scrapes CSV files for players, teams, games, box_score
- **Data_Clean.py** - Cleans up duplicate columns and rows, combines traditional/advanced box_scores
- **SQL_Creation.py** - Helps format the CSV files and put them into SQL, creates primary keys

#### `src/AppUtils/`
- **Config.py** - Includes context information for tables, columns, example queries, includes MySQL connection information (from .env)
- **DB.py** - Includes code for connecting and closing MySQL connections, executing queries, validating queries, and getting primary key information
- **Input.py** - Main code that is called in main.py to take user input, process, and direct it to correct file
- **Modification.py** - Includes code for processing modification queries and validating safety of them 
- **NLP.py** - Includes code to process user input using regex to gain information about user intent (query, explore, modify)
- **Translation.py** - Includes code to make calls to OpenAI, translate processed input into SQL, explain translation, and send to DB.py

#### Root Files
- **main.py** - Includes code to set up simple streamlit web interface to display results with pretty formatting, mostly make calls to Input.py
- **export_csv.py** - Exports the NBA database tables to CSV files
- **requirements.txt** - Required packages for entire app

## 🚀 Running Streamlit

### Data Files:

Simple Method (Recommended)
- **src/data/nba_database.sql** : This file contains the SQL script to just upload the data straight to your server
    - This will be much simpler and will bypass any glitches or uncoded changes to the tables (if any of my changes were at the csv level)

Manual Method:
```bash
 # Navigate to the utils director -> src/utils

# You will need to run three files:

# Collect the data
python data_scrape.py

# Perform cleaning
python data_clean.py

# Upload to server
python sql_upload.py
```

Virtual Environment:

### Virtual Environment

#### Creating and Activating

##### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

##### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

#### Configurations:
Change these values in your .env (in src/utils) file to match these variables inside src/utils/config.py

- You WILL need all of these for the code to function
```python
DB_CONFIG = {
    'host': os.getenv("DB_HOST"), # Hostname for your local SQL server
    'user': os.getenv("DB_USER"), # Username for your local SQL Server
    'password': os.getenv("DB_PASSWORD"), # Password for your local SQL server, should be in .env
    'port': os.getenv("DB_PORT"), # Port number you chose for SQL server
    'database': os.getenv("DB_NAME"), # Whatever the name of the database you uploaded the SQL files or converted csv files to on your SQL server
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Run the Application
```bash
# Make sure you are in the main directory
python -m streamlit run main.py
```
