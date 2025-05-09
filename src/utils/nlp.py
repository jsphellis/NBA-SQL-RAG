"""
nlp.py

This file contains functions for cleaning the user's input and
determining the intent of the query (schema exploration, data modification, or data query)
"""

import re


def user_input(input_string):
    """
    Cleans the user's input and determines the intent of the query
    """
    input_clean = input_string.strip()
    input_type = determine_intent(input_clean)

    return input_type, input_clean


def determine_intent(user_query):
    """
    Determines the intent of the user's input
    If it's a schema exploration or normal query - gets sent to translation.py,
    if it's a data modification - gets sent to modification.py
    """
    user_query = user_query.lower()

    schema_patterns = [
        r'\b(what|which|show|list|display)\b.*(tables|schema|columns|fields|structure)\b',
        r'\b(describe|explain)\b.*(table|structure)\b',
        r'\bhow.*(schema|structured|organized)\b',
        r'\b(what|which).*(attributes|fields|columns).*(table|have|contain)\b',
        r'\b(primary key|keys).*(of|for|in)\s+(?:the\s+)?(\w+)',
        r'\b(sample|example)\b.*(data|rows).*(from|in)\b.*\btable\b',
        r'\bshow.*\bdata\b.*\bfrom\b',
        r'\bgive.*\bsample\b.*\bfrom\b']

    modify_patterns = [
        r'\b(add|insert|create|put)\b',
        r'\b(update|modify|change|edit)\b',
        r'\b(delete|remove|drop)\b'
    ]

    for patt in schema_patterns:
        if re.search(patt, user_query):
            return "schema_explore"

    for patt in modify_patterns:
        if re.search(patt, user_query):
            return "data_modification"

    return "data_query"
