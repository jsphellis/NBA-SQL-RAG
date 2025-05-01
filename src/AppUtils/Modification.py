import re
from src.AppUtils.DB import Execute_SQL, Get_Primary_Keys
from src.AppUtils.Translation import Call_Language_Model, Validate_SQL
from src.AppUtils.Config import NBA_SCHEMA_CONTEXT, SAMPLE_DATA, EXAMPLE_QUERIES

def Handle_Data_Modification(user_input):
    """
    Process natural language requests for data modification (INSERT, UPDATE, DELETE)
    """
    prompt = f"""
        You are an expert SQL translator for an NBA database. Convert the following natural language request 
        into a valid MySQL data modification statement (INSERT, UPDATE, or DELETE).
        
        {NBA_SCHEMA_CONTEXT}
        
        Sample data:
        Players: {SAMPLE_DATA['players'][:2]}
        Teams: {SAMPLE_DATA['teams'][:2]}
        
        Example modification queries:
        1. "Add a new player named Michael Jordan": {EXAMPLE_QUERIES[14]}
        2. "Update Michael Jordan's team to the Lakers": {EXAMPLE_QUERIES[15]}
        3. "Delete the player with Person_ID 20777 (Added in example 1)": {EXAMPLE_QUERIES[16]}
        
        User Request: {user_input}
        
        Return only the SQL statement without any explanation. Use precise column names from the schema.
        If creating a new record, include all required fields with reasonable default values if not provided
        If updating records, include appropriate WHERE clauses to target specific records
        If deleting records, include a very specific WHERE clause to prevent accidental deletion of multiple records
    """
    
    sql_query = Call_Language_Model(prompt)
    is_valid, error_msg = Validate_SQL(sql_query)
    
    if not is_valid:
        return {
            "success": False,
            "error": error_msg,
            "original_request": user_input
        }
    
    return {
        "success": True,
        "sql_query": sql_query,
        "status": "Ready for confirmation",
        "explanation": f"This will modify data in the database. Please confirm by typing 'confirm' or modify the SQL query.",
        "original_request": user_input
    }

def Execute_Modification(sql_query):
    """
    Execute a data modification query with additional safety checks
    """
    if sql_query.strip().upper().startswith("DELETE") and "WHERE" not in sql_query.upper():
        return {
            "success": False,
            "error": "DELETE operations must include a WHERE clause for safety"
        }
        
    if sql_query.strip().upper().startswith("UPDATE") and "WHERE" not in sql_query.upper():
        return {
            "success": False,
            "error": "UPDATE operations must include a WHERE clause for safety"
        }
    
    result = Execute_SQL(sql_query)
    return result

def Verify_Modification(sql_query, execution_result):
    """
    Allows the user to verify the results of their modification
    """
    if not execution_result.get("success", False):
        return execution_result
    
    try:
        sql_upper = sql_query.upper()
        verification_sql = None
        
        if sql_upper.startswith("INSERT"):
            match = re.search(r"INSERT\s+INTO\s+(\w+)", sql_upper)
            if not match:
                return execution_result
            
            table_name = match.group(1).lower()
            
            pk_info = Get_Primary_Keys(table_name)
            if 'error' in pk_info or not pk_info.get('primary_keys'):
                verification_sql = f"SELECT * FROM {table_name} ORDER BY {pk_info.get('primary_keys', ['id'])[0]} DESC LIMIT 1"
            else:
                values_match = re.search(r"VALUES\s*\((.*?)\)", sql_query, re.IGNORECASE | re.DOTALL)
                if not values_match:
                    verification_sql = f"SELECT * FROM {table_name} ORDER BY {pk_info.get('primary_keys')[0]} DESC LIMIT 1"
                else:
                    values = values_match.group(1).split(',')
                    pk_columns = pk_info.get('primary_keys', [])
                    
                    pk_values = {}
                    col_match = re.search(r"INSERT\s+INTO\s+\w+\s*\((.*?)\)", sql_query, re.IGNORECASE | re.DOTALL)
                    if col_match:
                        columns = [c.strip() for c in col_match.group(1).split(',')]
                        for i, col in enumerate(columns):
                            if i < len(values) and col in pk_columns:
                                pk_values[col] = values[i].strip().strip("'\"")
                    
                    if pk_values:
                        where_clauses = []
                        for col, val in pk_values.items():
                            where_clauses.append(f"{col} = {val}")
                        verification_sql = f"SELECT * FROM {table_name} WHERE {' AND '.join(where_clauses)}"
                    else:
                        verification_sql = f"SELECT * FROM {table_name} ORDER BY {pk_info.get('primary_keys')[0]} DESC LIMIT 1"
        
        elif sql_upper.startswith("UPDATE"):
            match = re.search(r"UPDATE\s+(\w+)", sql_upper)
            if not match:
                return execution_result
            
            table_name = match.group(1).lower()
            
            where_match = re.search(r"WHERE\s+(.*?)(?:ORDER BY|LIMIT|$)", sql_query, re.IGNORECASE | re.DOTALL)
            if not where_match:
                verification_sql = f"SELECT * FROM {table_name} LIMIT 5"
            else:
                where_clause = where_match.group(1).strip()
                verification_sql = f"SELECT * FROM {table_name} WHERE {where_clause} LIMIT 5"
        
        elif sql_upper.startswith("DELETE"):
            match = re.search(r"DELETE\s+FROM\s+(\w+)", sql_upper)
            if not match:
                return execution_result
            
            table_name = match.group(1).lower()
            
            where_match = re.search(r"WHERE\s+(.*?)(?:ORDER BY|LIMIT|$)", sql_query, re.IGNORECASE | re.DOTALL)
            if not where_match:
                verification_sql = f"SELECT COUNT(*) as remaining_records FROM {table_name}"
            else:
                where_clause = where_match.group(1).strip()
                verification_sql = f"SELECT COUNT(*) as remaining_records FROM {table_name} WHERE {where_clause}"
        
        else:
            return execution_result
        
        verification_result = Execute_SQL(verification_sql)
        
        if verification_result.get("success", False):
            if sql_upper.startswith("DELETE"):
                count = verification_result.get("data", [{}])[0].get("remaining_records", 0)
                if count == 0:
                    verification_result["message"] = "Verification successful: All matching records were deleted."
                else:
                    verification_result["message"] = f"Verification: {count} similar records still exist in the database."
            else:
                verification_result["message"] = "Verification: Here are the affected records after your modification:"
            
            verification_result["original_change"] = execution_result.get("message", "")
            verification_result["affected_rows"] = execution_result.get("affected_rows", 0)
            
            return verification_result
        else:
            return execution_result
            
    except Exception as e:
        execution_result["verification_error"] = str(e)
        return execution_result
