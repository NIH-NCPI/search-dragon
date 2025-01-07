"""
Generate the final result response, and any final validation.
"""
from collections import Counter
from search_dragon import logger


def generate_response(
    data, search_url, more_results_available
):
    logger.info(f"Count fetched_data {len(data)}")

    ontology_counts, results_count = get_code_counts(data)
    cleaned_data = curate_data(data)

    structured_data = {
        "search_query": search_url,
        "results": cleaned_data,
        "results_per_ontology": ontology_counts,
        "results_count": results_count,
        "more_results_available": more_results_available,
    }
    return structured_data


def get_code_counts(data):
    """
    Count occurrences of each ontology in the code field of the data.
    """
    # Extract ontology prefixes
    count = Counter(item["ontology_prefix"] for item in data)
    ontology_counts = dict(count)

    results_counts = len(data)
    return ontology_counts, results_counts


def remove_duplicates(data):
    """
    Some ontologies include codes from within other ontologies. Filter out those
    api results where the ontology_prefix(code prefix ex: MONDO) does not match
    the ontology code for the record.
    """
    filtered_data = []
    excluded_data = []
    for item in data:
        ontology_prefix = item.get("ontology_prefix")
        code = item.get("code")

        # Check if code starts with the ontology prefix, if it does not, excude and log the record
        if not code.startswith(ontology_prefix):
            excluded_data.append(item)
        else:
            filtered_data.append(item)

    message = f"Records({(len(excluded_data))}) are excluded because the code does not start with the ontology_prefix"
    logger.info(message)

    return filtered_data

def validate_data(data):
    """
    Handle nulls in the data. Ensure all missing data is handled and returned
    with the appropriate dtype. Specifically handles `description` as an array.
    """
    default_values = {
        "code": "",
        "system": "",
        "code_iri": "",
        "display": "",
        "description": [],  # Default to an empty list
        "ontology_prefix": "",
    }

    validated_data = []
    for item in data:
        validated_item = {}
        for key, default in default_values.items():
            value = item.get(key, default)

            if key == "description" and not isinstance(value, list):
                # Convert `description` to a list if it's not already
                value = [value] if value else []

            validated_item[key] = value

        validated_data.append(validated_item)

    return validated_data

def curate_data(data):
    """
    NULLs have been handled, no duplicates, data has the expected types etc.
    """
    logger.info(f"data length {len(data)}")

    # handle duplicates
    dup_cleaned = remove_duplicates(data)

    # sanity check

    logger.info(f"data length after removing duplicates {len(dup_cleaned)}")

    # handle nulls and data types
    cleaned_data = validate_data(dup_cleaned)

    return cleaned_data
