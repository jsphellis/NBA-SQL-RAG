import streamlit as st
import pandas as pd
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.AppUtils.Input import Handle_Query

st.set_page_config(
    page_title="NBA Database Explorer",
    page_icon="🏀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stTextInput input {
        font-size: 16px;
    }
    .stButton button {
        background-color: #17408B;
        color: white;
    }
    .query-history {
        margin-top: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f0f0;
    }
    .results-area {
        margin-top: 15px;
        padding: 15px;
        border-radius: 5px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        margin-top: 15px;
    }
    .sql-code {
        background-color: #272822;
        padding: 10px;
        border-radius: 5px;
        color: #f8f8f2;
    }
    .modification-warning {
        color: #c41a1a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def Init_Session_State():
    """
    Initializes session state variables if they don't exist
    """
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []

def Handle_User_Query(query):
    """
    Processes user query and returns results
    """
    with st.spinner('Processing your query...'):
        result = Handle_Query(query)
        
        st.session_state.query_history.append({
            "query": query,
            "result": result,
            "timestamp": time.strftime("%H:%M:%S")
        })
        
        return result

def Display_Data_Results(result):
    """
    Displays data query results
    """
    if 'formatted_result' in result:
        st.markdown("### Results")
        if 'sql_query' in result:
            st.markdown("#### SQL Query Used")
            st.markdown(f"<div class='sql-code'>{result['sql_query']}</div>", unsafe_allow_html=True)
            
            if 'explanation' in result:
                with st.expander("SQL Explanation"):
                    st.write(result['explanation'])
        
        if 'raw_result' in result and 'data' in result['raw_result'] and result['raw_result']['data']:
            df = pd.DataFrame(result['raw_result']['data'])
            st.dataframe(df, use_container_width=True)
        else:
            st.markdown(result['formatted_result'])
    else:
        st.warning("No results to display.")

def Execute_Modification_Directly(result):
    """
    Executes a modification query
    """
    st.markdown("### Data Modification")
    
    if 'sql_query' not in result:
        st.error("No SQL query found in the result")
        return
    
    sql_query = result['sql_query']
    st.markdown("#### SQL Query")
    st.markdown(f"<div class='sql-code'>{sql_query}</div>", unsafe_allow_html=True)
    
    if sql_query.strip().upper().startswith("DELETE"):
        try:
            from src.AppUtils.DB import Execute_SQL
            import re
            
            where_match = re.search(r"WHERE\s+(.*?)(?:;|$)", sql_query, re.IGNORECASE | re.DOTALL)
            
            if where_match:
                where_clause = where_match.group(1).strip()
                check_query = f"SELECT * FROM players WHERE {where_clause} LIMIT 1"
                
                st.write("Checking if player exists...")
                check_result = Execute_SQL(check_query)
                
                if check_result.get("success", False) and check_result.get("data"):
                    player_data = check_result.get("data")[0]
                    st.success(f"Found player: {player_data.get('FIRST_NAME', '')} {player_data.get('LAST_NAME', '')}")
                else:
                    st.warning("Player not found in database. Deletion may have no effect.")
        except Exception as e:
            st.error(f"Error checking player: {str(e)}")
    
    st.write("Executing SQL modification...")
    
    try:
        from src.AppUtils.Modification import Execute_Modification, Verify_Modification
        execution_result = Execute_Modification(sql_query)
        
        if execution_result.get("success", False):
            st.success(f"Success: {execution_result.get('message', 'Operation completed')}")
            verification_result = Verify_Modification(sql_query, execution_result)
            
            if verification_result.get("success", False):
                if verification_result.get("data"):
                    st.markdown("#### Verification Result")
                    df = pd.DataFrame(verification_result.get("data", []))
                    st.dataframe(df, use_container_width=True)
                
                st.success(verification_result.get("message", "Verification successful"))
            else:
                st.warning("Verification could not confirm the changes")
        else:
            st.error(f"Error: {execution_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"Error executing SQL: {str(e)}")

def main():
    """
    Main function to run the NBA database explorer
    """
    Init_Session_State()
    
    st.title("🏀 NBA Database Explorer")
    
    query = st.text_input("What would you like to know about the NBA?", placeholder="For example: 'Who are the top 10 scorers in the NBA?' or 'Show me columns in the players table'")
    
    if st.button("Submit", key="submit_query"):
        if query:
            result = Handle_User_Query(query)
            
            query_type = result.get('query_type')
            if query_type == 'schema_explore':
                Display_Data_Results(result)
            elif query_type == 'data_query':
                Display_Data_Results(result)
            elif query_type == 'data_modification':
                Execute_Modification_Directly(result)
            else:
                st.warning(f"Unrecognized query type: {query_type}")
        else:
            st.warning("Please enter a query.")
    
if __name__ == "__main__":
    main()
