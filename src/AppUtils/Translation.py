import re
import openai
from src.AppUtils.Config import LLM_MODEL, LLM_TEMPERATURE, NBA_SCHEMA_CONTEXT, EXAMPLE_QUERIES, SAMPLE_DATA
from src.AppUtils.DB import Validate_SQL

def Translate_To_SQL(query, schema_info=None):
    """
    Translates the user's question to a valid SQL query
    """
    prompt = f"""
        You are an expert SQL translator for an NBA database. Convert the following natural language question to a valid MySQL query.

        {NBA_SCHEMA_CONTEXT}

        Example NBA data:
        Players: {SAMPLE_DATA['players'][:1]}
        Teams: {SAMPLE_DATA['teams'][:1]}
        Box scores: {SAMPLE_DATA['box_score'][:1]}

        Example exploration:
        Examples:
            - "What tables are in the database?" -> "SHOW TABLES;"
            - "Show me the columns in the players table" -> "DESCRIBE players;"
            - "Tell me about the teams table structure" -> "SHOW COLUMNS FROM teams;"
            - "Give me sample data from the games table" -> "SELECT * FROM games LIMIT 5;"

        Example queries:
            - "Show me the 5 tallest players": {EXAMPLE_QUERIES[6]}
            - "List 7 Lakers players": {EXAMPLE_QUERIES[7]}
            - "Show me the 5 teams with the most players": {EXAMPLE_QUERIES[8]}
            - "Show top scorers, limit 10, ordered by average points descending": {EXAMPLE_QUERIES[11]}
            - "Get player stats by team, limit 10, ordered by average points descending": {EXAMPLE_QUERIES[12]}
            - "Find five teams and their average points, limit 5, ordered by average points descending": {EXAMPLE_QUERIES[13]}

        User Question: {query}

        Return only the SQL query without any explanation.
    """
    sql_query = Call_Language_Model(prompt)
    print("Translated SQL")
    print(sql_query)
    is_valid, error_msg = Validate_SQL(sql_query)

    if is_valid:
        return {
            "success": True,
            "sql_query": sql_query,
            "explanation": Generate_SQL_Explanation(sql_query, query)
        }
    else:
        return {
            "success": False,
            "error": error_msg,
            "original_query": query
        }
    
def Build_Sample_Query(query_type=None):
    """
    Generates a sample SQL query for the NBA database
    """
    type_guidance = ""
    if query_type:
        if query_type == "player_stats":
            type_guidance = "Generate a query that shows player statistics."
        elif query_type == "team_rankings":
            type_guidance = "Generate a query that ranks teams based on performance."
    
    prompt = f"""
        You are an expert sample SQL query builder for an NBA database.

        {NBA_SCHEMA_CONTEXT}

        Example NBA data:
        Players: {SAMPLE_DATA['players'][:1]}
        Teams: {SAMPLE_DATA['teams'][:1]}
        Box scores: {SAMPLE_DATA['box_score'][:1]}

        Example queries:
        1. "Show me the tallest players": {EXAMPLE_QUERIES[6]}
        2. "List Lakers players": {EXAMPLE_QUERIES[7]}
        3. "Count players by team": {EXAMPLE_QUERIES[8]}
        4. "Show top scorers": {EXAMPLE_QUERIES[11]}
        5. "Get player stats by team": {EXAMPLE_QUERIES[12]}
        6. "Find all teams and their average points": {EXAMPLE_QUERIES[13]}
        
        {type_guidance}
        
        Return only the SQL query without any explanation.
    """
    
    try:
        sql_query = Call_Language_Model(prompt)
        is_valid, error_msg = Validate_SQL(sql_query)

        if is_valid:
            explanation = Generate_SQL_Explanation(sql_query, "Sample query")
            return {
                "success": True,
                "sql_query": sql_query,
                "explanation": explanation
            }
        else:
            return {
                "success": False,
                "error": error_msg,
                "original_query": "Sample query"
            }
    except Exception as e:
        print(f"Error generating sample query: {e}")
        return {
            "success": False,
            "error": f"Error generating sample query: {e}",
            "original_query": "Sample query"
        }
    
def Call_Language_Model(prompt):
    try:
        
        response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert SQL translator for an NBA database. Generate only valid MySQL SQL queries without explanations or comments."},
                {"role": "user", "content": prompt}
            ],
            temperature=LLM_TEMPERATURE 
        )
        content = response.choices[0].message.content
        content = re.sub(r'^```sql\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^```\s*', '', content)
        content = re.sub(r'\s*```$', '', content)

        return content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "SELECT * FROM players LIMIT 10"
    
def Format_SQL_Results(result):
    """
    Formats SQL query results into a human-readable format
    """
    if not result.get("success", False):
        return f"Error executing query: {result.get('error', 'Unknown error')}"
    
    result_type = result.get("result_type")
    
    if result_type == "data":
        data = result.get("data", [])
        column_names = result.get("column_names", [])
        row_count = result.get("row_count", 0)
        
        if not data:
            return "Query executed successfully, but no data was returned."
        
        output = "| " + " | ".join(column_names) + " |\n"
        output += "|" + "---|" * len(column_names) + "\n"
        
        for row in data:
            row_values = [str(row.get(col, "")) for col in column_names]
            output += "| " + " | ".join(row_values) + " |\n"
        
        output += f"\n{row_count} rows returned."
        return output
    
    elif result_type == "modification":
        affected_rows = result.get("affected_rows", 0)
        return f"Query executed successfully. {affected_rows} rows affected."
    
    return "Unrecognized result type."

def Format_Schema_Results(result):
    """
    Formats schema results from translated queries into human-readable markdown
    """
    if not result.get('success', False):
        return f"Error: {result.get('error', 'Unknown error')}"
    
    data = result.get('data', [])
    if not data:
        return "No results found."
    
    columns = list(data[0].keys()) if data else []
    response = "| " + " | ".join(columns) + " |\n"
    response += "|" + "---|" * len(columns) + "\n"
    
    for row in data:
        row_values = []
        for col in columns:
            val = row.get(col, '')
            if val is None:
                val = 'NULL'
            elif isinstance(val, (list, dict)):
                val = str(val)
            row_values.append(str(val))
        
        response += "| " + " | ".join(row_values) + " |\n"
    
    return response
    
def Generate_SQL_Explanation(sql_query, original_query):
    """
    Generates a human-readable explanation of what the SQL query does
    """
    prompt = f"""
        You are an expert at explaining SQL queries to users who might not be familiar with SQL.
        Take the following natural language question and the corresponding SQL query, and explain what the SQL does:
        
        Original question: "{original_query}"

        SQL query: {sql_query}

        {NBA_SCHEMA_CONTEXT}

        Do not number your explanation in steps, just have a newline for each line in the sql query. Keep it short and concise.
    """
    try:
        response = openai.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": """You are an expert at explaining natural language to SQL translation"""},
                {"role": "user", "content": prompt}
            ],
            temperature=LLM_TEMPERATURE 
        )
        content = response.choices[0].message.content

        return content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
    
    return "SQL query generated from your question."