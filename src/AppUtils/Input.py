from src.AppUtils.NLP import User_Input
from src.AppUtils.Translation import Translate_To_SQL, Format_SQL_Results, Format_Schema_Results
from src.AppUtils.DB import Execute_SQL
from src.AppUtils.Modification import Handle_Data_Modification

def Handle_Query(user_input):
    """
    Handles the user's input and returns the results of the query (includes processing, translation, execution, and formatting)
    """
    user_intent, clean_query = User_Input(user_input)

    if user_intent == "schema_explore":
        print("Schema exploration")
        translation_result = Translate_To_SQL(clean_query)
        
        if translation_result["success"]:
            sql_query = translation_result["sql_query"]
            execution_result = Execute_SQL(sql_query)
            
            if execution_result["success"]:
                formatted_result = Format_Schema_Results(execution_result)
                
                return {
                    "query_type": user_intent,
                    "sql_query": sql_query,
                    "explanation": translation_result.get("explanation", ""),
                    "raw_result": execution_result,
                    "formatted_result": formatted_result
                }
            else:
                return {
                    "query_type": user_intent,
                    "sql_query": sql_query,
                    "error": execution_result["error"],
                    "status": "Execution failed"
                }
    elif user_intent == "data_query":
        translation_result = Translate_To_SQL(clean_query)
        
        if translation_result["success"]:
            sql_query = translation_result["sql_query"]
            execution_result = Execute_SQL(sql_query)
            
            if execution_result["success"]:
                formatted_result = Format_SQL_Results(execution_result)
                
                return {
                    "query_type": user_intent,
                    "processed_query": clean_query,
                    "sql_query": sql_query,
                    "explanation": translation_result["explanation"],
                    "raw_result": execution_result,
                    "formatted_result": formatted_result,
                    "status": "Executed successfully"
                }
            else:
                return {
                    "query_type": user_intent,
                    "processed_query": clean_query,
                    "sql_query": sql_query,
                    "error": execution_result["error"],
                    "status": "Execution failed"
                }
        else:
            return {
                "query_type": user_intent,
                "processed_query": clean_query,
                "error": translation_result["error"],
                "status": "Translation failed"
            }
    elif user_intent == "data_modification":
        modification_result = Handle_Data_Modification(clean_query)
        
        if modification_result["success"]:
            return {
                "query_type": user_intent,
                "processed_query": clean_query,
                "sql_query": modification_result["sql_query"],
                "status": "Ready for confirmation",
                "explanation": modification_result["explanation"]
            }
        else:
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
