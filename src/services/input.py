"""
input.py

This file contains the functions for handling the user's input
This means acquiring the intent from nlp.py, then sending the
query to the appropriate service.
"""

from src.services.translation import translate_to_sql, format_sql_results, format_schema_results
from src.services.db import execute_sql
from src.services.modification import handle_data_modification

def user_input(query):
    """
    Processes the user's input to determine their intent and clean the query
    Returns a tuple of (intent, cleaned_query)
    """
    query = query.lower().strip()

    schema_keywords = ['show', 'describe', 'structure', 'schema', 'tables', 'columns']
    if any(keyword in query for keyword in schema_keywords):
        return "schema_explore", query

    modification_keywords = ['insert', 'update', 'delete', 'add', 'remove', 'change']
    if any(keyword in query for keyword in modification_keywords):
        return "data_modification", query

    return "data_query", query

def handle_query(user_query):
    """
    Handles the user's input and returns the results of the query 
    (includes processing, translation, execution, and formatting)
    """
    user_intent, clean_query = user_input(user_query)

    if user_intent == "schema_explore":
        print("Schema exploration")
        translation_result = translate_to_sql(clean_query)

        if translation_result["success"]:
            sql_query = translation_result["sql_query"]
            execution_result = execute_sql(sql_query)

            if execution_result["success"]:
                formatted_result = format_schema_results(execution_result)

                return {
                    "query_type": user_intent,
                    "sql_query": sql_query,
                    "explanation": translation_result.get("explanation", ""),
                    "raw_result": execution_result,
                    "formatted_result": formatted_result
                }
            return {
                "query_type": user_intent,
                "sql_query": sql_query,
                "error": execution_result["error"],
                "status": "Execution failed"
            }
    elif user_intent == "data_query":
        translation_result = translate_to_sql(clean_query)

        if translation_result["success"]:
            sql_query = translation_result["sql_query"]
            execution_result = execute_sql(sql_query)

            if execution_result["success"]:
                formatted_result = format_sql_results(execution_result)

                return {
                    "query_type": user_intent,
                    "processed_query": clean_query,
                    "sql_query": sql_query,
                    "explanation": translation_result["explanation"],
                    "raw_result": execution_result,
                    "formatted_result": formatted_result,
                    "status": "Executed successfully"
                }
            return {
                "query_type": user_intent,
                "processed_query": clean_query,
                "sql_query": sql_query,
                "error": execution_result["error"],
                "status": "Execution failed"
            }
        return {
            "query_type": user_intent,
            "processed_query": clean_query,
            "error": translation_result["error"],
            "status": "Translation failed"
        }
    elif user_intent == "data_modification":
        modification_result = handle_data_modification(clean_query)

        if modification_result["success"]:
            return {
                "query_type": user_intent,
                "processed_query": clean_query,
                "sql_query": modification_result["sql_query"],
                "status": "Ready for confirmation",
                "explanation": modification_result["explanation"]
            }
        return {
            "query_type": user_intent,
            "processed_query": clean_query,
            "error": modification_result["error"],
            "status": "Translation failed"
        }
    else:
        return {
            "query_type": user_intent,
            "processed_query": clean_query,
            "status": "Unrecognized intent"
        }
