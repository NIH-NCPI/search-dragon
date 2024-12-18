"""
Purpose: define apis
    define harmonization
    define building of url(word search, not filtering)

Level to filter? Return data for front end to cache and leave the filter/sort up to them

Any need to limit results at the ontology api request level? 

Response format - collected from the API
    Code
    Ontology
    Curie
    Code Display
    Code UrL (https://ontobee.org/ontology/NCIT?iri=http://purl.obolibrary.org/obo/NCIT_C17459)
    Code Description
Front end response additions added to the data in search.py
    Number of codes (total)
    Number of codes(per ontology)
    Response limit

Does there need to be a function that recognizes a code searched for, rather than a display/keyword?
"""
from search_dragon.external_apis import OntologyAPI
from collections import Counter
from search_dragon import logger

OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
OLS_API = "ols"
OLS_NAME = "Ontology Lookup Service"

class OLSSearchAPI(OntologyAPI):
    def __init__(self):
        super().__init__(base_url=OLS_API_BASE_URL, api_id=OLS_API, api_name=OLS_NAME)

    # Set variables for each api here
    # Each api with own file in sources
    # If no ontologies - include only the special ontology list

    def format_keyword(self, keywords):
        """
        Will ensure the keyword is acceptable and apply any fuzzy match
        q=cancer+brain%20cancer
        Setting keyword as a list for eventual fuzzy match capability
        """

        keywords = keywords.replace(" ","%20")

        keyword_param=f"q={keywords}"

        return keyword_param
    
    def get_ontology_keys(self, ontology_data):
        """ """
        ontology_keys = ontology_data.keys()
        
        ontology_keys_list = list(ontology_keys)

        return ontology_keys_list

    def format_ontology(self, ontology_data):
        """
        Add the included ontologies to the search url. User preferred ontologies
        will be selected for in the combined data curation stage.
        """
        #TODO get the list from the firestore
        included_ontologies = self.get_ontology_keys(ontology_data)
        logger.info(f"onto keys {included_ontologies}")

        formatted_ontologies = ",".join(included_ontologies)
        
        ontology_param =f"ontology={formatted_ontologies}"
        
        return ontology_param

    def build_url(self, keywords, ontology_data):
        """Expected format:
        http://www.ebi.ac.uk/ols4/api/search?q={q}&ontology={ontology}
        http://www.ebi.ac.uk/ols4/api/search?q={q}+{q}&ontology={ontology},{ontology}

        # account for empty query params
        # Maybe make the query params in the format functions
        """
        url_blocks = []
        url_blocks.append(f"{self.base_url}search?")

        keyword_param = self.format_keyword(keywords)
        ontology_param = self.format_ontology(ontology_data)

        # Join the query params with & then join the params to the base url
        url_blocks.append("&".join([keyword_param,ontology_param]))
        complete_url = "".join(url_blocks)

        return complete_url
    
    def harmonize_data(self, raw_results, ontology_data):
        # If raw_results is a list, iterate over it
        if isinstance(raw_results, list):
            return [self.harmonize_data(item, ontology_data) for item in raw_results]
        
        harmonized_data = {
            "code": raw_results.get("obo_id"),
            "system": None, #TODO get from firestore
            "code_iri": raw_results.get("iri"),
            "display": raw_results.get("label"),
            "description": raw_results.get("description", []),
            "ontology_prefix": raw_results.get("ontology_prefix"),

        }

        return harmonized_data
    
    # # TODO 
    # def apply_fuzzy_match():
    #     """Create more keywords to search for."""
    #     pass