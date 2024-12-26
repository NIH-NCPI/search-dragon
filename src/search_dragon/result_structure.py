"""
Generate the final result response, and any final validation.
"""
from collections import Counter

def generate_response(data, search_url, ontology_list=None):
    ontology_counts, results_count = get_code_counts(data)

    structured_data = {"search_query": search_url,
                       "results": data,
                       "results_per_ontology": ontology_counts,
                       "results_count": results_count}
    return structured_data

def get_code_counts(data):
    """
    Count occurrences of each ontology in the code field of the data.
    """
    # Extract ontology prefixes from the 'code' field
    count = Counter(item["code"].split(":")[0] for item in data)
    ontology_counts = dict(count)
    
    results_counts = len(data)
    return ontology_counts, results_counts

def validate_response():
    """
    NULLs have been handled, no duplicates etc.
    """
    pass


