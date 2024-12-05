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

from common import OLS_API, OLS_API_BASE_URL, OLS_NAME
from filters import format_keyword, format_ontology
from typing import List


class OntologyAPI:
    def __init__(self, base_url, api_id, api_name):
        self.base_url = base_url
        self.api_id = api_id
        self.api_name = api_name

    def get_api_instance(search_api):
        if search_api == "ols":
            return OLSSearchAPI()
        else:
            pass

class OLSSearchAPI(OntologyAPI):
    def __init__(self):
        super().__init__(base_url=OLS_API_BASE_URL, api_id=OLS_API)

    def build_url(self, keywords: List, ontologies: List):
        """Expected format:
        http://www.ebi.ac.uk/ols4/api/search?q={q}&ontology={ontology}
        http://www.ebi.ac.uk/ols4/api/search?q={q}+{q}&ontology={ontology},{ontology}
        """
        final_url_list = []
        query_params = []

        final_url_list.append(f"{self.base_url}search?")

        if keywords:
            # q=cancer+brain%20cancer
            # Setting keyword as a list for eventual fuzzy match capability
            formatted_keywords = "+".join(format_keyword(kw) for kw in keywords)
            query_params.append(f"q={formatted_keywords}")

        if ontologies:
            # ontology=MONDO,BTO
            # Might not need this. Seems we want all ontology results at this stage - for counts
            formatted_ontologies = ",".join(format_ontology(ont) for ont in ontologies)
            query_params.append(f"ontology={formatted_ontologies}")

        # Join the query params with & then join the params to the base url
        final_url_list.append("&".join(query_params))
        final_url = "".join(final_url_list)

        return final_url

    def harmonize_data(self, raw_results):
        harmonized_data = {
            "ontology_code": raw_results["ontologyId"],
        }

        return harmonized_data
