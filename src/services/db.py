"""
db.py

This file contains functions for connecting to the MySQL database
and executing SQL queries
"""

import re
import mysql.connector
from mysql.connector import Error
from openai import APIError, RateLimitError, APIConnectionError
from src.utils.config import DB_CONFIG, DANGEROUS_SQL_KEYWORDS

def get_connection():
    """
    Establishes connection to MySQL database
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def close_connection(connection, cursor=None):
    """
    Safely close database connection and cursor.
    """
    if cursor:
        try:
            cursor.close()
        except Error as e:
            print(f"Error closing cursor: {e}")

    if connection:
        try:
            connection.close()
        except Error as e:
            print(f"Error closing connection: {e}")


def execute_query(
        query,
        params=None,
        fetch=True,
        commit=False,
        dictionary=True):
    """
    Execute a SQL query and return the results.
    """
    connection = get_connection()
    if not connection:
        return {
            "success": False,
            "error": "Failed to connect to the database"
        }

    cursor = None
    try:
        cursor = connection.cursor(dictionary=dictionary)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            results = cursor.fetchall()
            column_names = [
                desc[0] for desc in cursor.description] if cursor.description else []

            result_info = {
                "success": True,
                "result_type": "data",
                "data": results,
                "column_names": column_names,
                "row_count": len(results),
                "message": f"Query returned {len(results)} rows."
            }
        elif commit:
            connection.commit()
            affected_rows = cursor.rowcount

            result_info = {
                "success": True,
                "result_type": "modification",
                "affected_rows": affected_rows,
                "message": f"Query executed successfully. {affected_rows} rows affected."}
        else:
            result_info = {
                "success": True,
                "result_type": "executed",
                "message": "Query executed successfully."
            }

        close_connection(connection, cursor)
        return result_info

    except Error as e:
        error_message = str(e)
        close_connection(connection, cursor)
        return {
            "success": False,
            "error": error_message
        }
    except (APIError, RateLimitError, APIConnectionError) as e:
        close_connection(connection, cursor)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


def execute_sql(sql_query):
    """
    Executes a SQL query and returns the results or affected rows (modification)
    """
    sql_upper = sql_query.strip().upper()

    if sql_upper.startswith(("SHOW", "DESCRIBE", "DESC", "EXPLAIN")):
        query_type = "SCHEMA"
    else:
        query_type = "SELECT"
        if sql_upper.startswith("INSERT"):
            query_type = "INSERT"
        elif sql_upper.startswith("UPDATE"):
            query_type = "UPDATE"
        elif sql_upper.startswith("DELETE"):
            query_type = "DELETE"

    if query_type == "DELETE":
        try:
            connection = get_connection()
            if not connection:
                return {
                    "success": False,
                    "error": "Failed to connect to database for DELETE operation"}

            cursor = connection.cursor()
            cursor.execute(sql_query)
            connection.commit()

            affected_rows = cursor.rowcount

            result = {
                "success": True,
                "result_type": "modification",
                "affected_rows": affected_rows,
                "message": f"DELETE executed successfully. {affected_rows} rows affected."}

            cursor.close()
            connection.close()
            return result

        except (APIError, RateLimitError, APIConnectionError) as e:
            return {
                "success": False,
                "error": f"Error executing DELETE: {str(e)}"
            }

    if query_type == "SCHEMA":
        return execute_query(sql_query, fetch=True, commit=False)
    elif query_type == "SELECT":
        result = execute_query(sql_query, fetch=True, commit=False)
    else:
        result = execute_query(sql_query, fetch=False, commit=True)

    return result


def validate_sql(sql_query):
    """
    Ensures that the SQL query is valid, makes sure UPDATE and DELETE queries have a WHERE clause
    """
    print("Validating SQL")
    print(sql_query)
    for keyword in DANGEROUS_SQL_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', sql_query.upper()):
            return False, f"Query contains disallowed operation: {keyword}"

    try:
        parts = sql_query.strip().upper().split()
        if not parts:
            return False, "Empty query"

        allowed_commands = [
            'SELECT',
            'INSERT',
            'UPDATE',
            'DELETE',
            'SHOW',
            'DESCRIBE',
            'DESC',
            'EXPLAIN']

        if parts[0] not in allowed_commands:
            return False, f"""
                Query must start with one of {', '.join(allowed_commands)}, found: {parts[0]}
            """

        return True, ""
    except (APIError, RateLimitError, APIConnectionError) as e:
        return False, f"SQL validation error: {str(e)}"

def get_primary_keys(table_name):
    """
    Gets primary key information for a specific table
    """
    try:
        print(f"Getting primary keys for table: {table_name}")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        sanitized_table = ''.join(
            c for c in table_name if c.isalnum() or c == '_')

        cursor.execute("SHOW TABLES LIKE %s", (sanitized_table,))
        if not cursor.fetchone():
            return {"error": f"Table '{table_name}' not found"}

        cursor.execute(f"DESCRIBE {sanitized_table}")
        columns = cursor.fetchall()
        primary_keys = [col["Field"] for col in columns if col["Key"] == "PRI"]

        if primary_keys:
            placeholders = ", ".join(primary_keys)
            cursor.execute(
                f"SELECT {placeholders} FROM {sanitized_table} LIMIT 5")
            examples = cursor.fetchall()
        else:
            examples = []

        result = {
            "query_type": "schema_explore",
            "result_type": "primary_keys",
            "table": sanitized_table,
            "primary_keys": primary_keys,
            "example_values": examples
        }

        cursor.close()
        connection.close()

        return result
    except Error as e:
        return {"error": f"Database error: {e}"}
