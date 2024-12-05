#base class - changes per api
def format_keyword():
    """Will ensure the keyword is acceptable and apply any fuzzy match"""
    pass

def format_ontology():
    """
    Will ensure the ontology is acceptable and filter on users choices
    May not need.
    - Filtering down to user preferred ontologies after counts are made in result_structure.py
    """
    pass

def remove_duplicate_responses():
    """
    Searching multiple APIs with similar Ontologies will result in duplicate codes 
    being returned.
    """
    pass

# # TODO
# def validate_keyword():
#     pass

# # TODO
# def validate_ontology():
#     pass

# # TODO 
# def apply_fuzzy_match():
#     """"""
#     pass

# # TODO
# def rank_ontology():
#     """
#     We may want to add the ability to sort the ontology by Domain(observation,condition),
#     or standard/reliability.

#     Or if the ontology api requests are run in parallel  - Sort results back into order
#     sent by the frontend request?  - This might go in result_structure.py instead
#     """


