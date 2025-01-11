"""
Generate the final result response, and any final validation.
"""
from collections import Counter
from search_dragon import logger


def generate_response(
    data, search_url, more_results_available, api_instances
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



def remove_duplicates(self, data):
    """
    Remove duplicate records where the 'uri' field is the same.

    Args:
        data (list): List of records to filter.

    Returns:
        list: Filtered data with duplicates removed.
    """
    seen_uris = set()
    filtered_data = []
    excluded_data = []

    for item in data:
        uri = item.get("code_iri")
        if uri in seen_uris:
            excluded_data.append(item)
        else:
            seen_uris.add(uri)
            filtered_data.append(item)

    # Log the excluded records count
    message = (
        f"Records({len(excluded_data)}) were excluded as duplicates based on 'uri'.{excluded_data}"
    )
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

    # handle nulls and data types
    cleaned_data = validate_data(data)

    return cleaned_data
