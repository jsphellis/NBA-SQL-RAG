import re

def User_Input(input_string):
    """
    Cleans the user's input and determines the intent of the query
    """
    input_clean = input_string.strip()
    input_type = Determine_Intent(input_clean)

    return input_type, input_clean

def Determine_Intent(user_input):
    """
    Determines the intent of the user's input (if it's a schema exploration or normal query - gets sent to Translation.py, if it's a data modification - gets sent to Modification.py)
    """
    user_input = user_input.lower()

    schema_patterns = [
        r'\b(what|which|show|list|display)\b.*(tables|schema|columns|fields|structure)\b',
        r'\b(describe|explain)\b.*(table|structure)\b',
        r'\bhow.*(schema|structured|organized)\b',
        r'\b(what|which).*(attributes|fields|columns).*(table|have|contain)\b',
        r'\b(primary key|keys).*(of|for|in)\s+(?:the\s+)?(\w+)',
        r'\b(sample|example)\b.*(data|rows).*(from|in)\b.*\btable\b',
        r'\bshow.*\bdata\b.*\bfrom\b',
        r'\bgive.*\bsample\b.*\bfrom\b'
    ]

    modify_patterns = [
        r'\b(add|insert|create|put)\b',
        r'\b(update|modify|change|edit)\b',
        r'\b(delete|remove|drop)\b'
    ]

    for patt in schema_patterns:
        if re.search(patt, user_input):
            return "schema_explore"
    
    for patt in modify_patterns:
        if re.search(patt, user_input):
            return "data_modification"
        
    return "data_query"