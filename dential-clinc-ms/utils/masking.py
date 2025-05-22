# utils/masking.py

def mask_db_results_keys_only(db_results):
    """
    Returns only column names from the DB results that have non-null values.
    Useful for understanding what kind of data is returned without exposing actual values.
    """
    if not db_results or not isinstance(db_results, list):
        return "No results"
    
    # Extract only keys that have non-None values in the first row
    row = db_results[0]
    non_null_keys = [key for key, value in row.items() if value is not None]

    return f"Result keys (non-null only): {non_null_keys}"


def mask_db_results_values(db_results):
    """
    Masks all values in DB results with <MASK> while retaining structure.
    """
    if not db_results:
        return "No results"
    
    return [{key: "<MASK>" for key in row} for row in db_results]

def replace_placeholders(answer, db_results):
    """
    Replaces LLM-safe placeholders in the answer with actual DB values.
    """
    if not db_results or not isinstance(db_results, list):
        return answer

    row = db_results[0]
    for key, value in row.items():
        placeholder = f"[value of {key} from the database results]"
        answer = answer.replace(placeholder, str(value))

    return answer