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

```bash
# Navigate to the main directory
python -m streamlit run main.py
```