
"""
This file holds data cleaning and transformation functions that are not source
api specific.

Examples: Filtering for or against attributes(ontologies), validation, and sorting
of combined api data.

"""
def curate_combined_data(combined_data, ontology_list):
    return combined_data

def remove_duplicate_responses():
    """
    Searching multiple APIs with similar Ontologies will result in duplicate codes 
    being returned.
    """
    pass
 
def count_results_per_ontology():
    pass

# # TODO
# def validate_keyword():
#     pass

# # TODO
# def validate_ontology():
#     pass

# # TODO
# def rank_ontology():
#     """
#     We may want to add the ability to sort the ontology by Domain(observation,condition),
#     or standard/reliability.

#     Or if the ontology api requests are run in parallel  - Sort results back into order
#     sent by the frontend request?  - This might go in result_structure.py instead
#     """



