"""
Provides the modular framework for searching across multiple ontology APIs.
"""

from search_dragon import logger
from search_dragon.external_apis import OntologyAPI
from search_dragon.external_apis.ols_api import OLSSearchAPI
from search_dragon.result_structure import generate_response
import argparse

SEARCH_APIS = [{"ols": OLSSearchAPI}]

def get_api_instance(search_api_list=None):
    '''Creates instances of ontology API classes based on the provided list of APIs. If no list is provided, instances of all available APIs are created.

    Args:
    search_api_list: List of API names to initialize. Defaults to None (initialize all available APIs).
    
    Returns:
    api_instances: A list of instantiated API classes.
    '''
    api_instances = []

    if search_api_list is None:
        for api_dict in SEARCH_APIS:
            for api_class in api_dict.values():
                api_instances.append(api_class())
    else:
        # Process only the APIs in the provided list
        for search_api in search_api_list:
            for api_dict in SEARCH_APIS:
                if search_api in api_dict:
                    api_instances.append(api_dict[search_api]())
                    break
            else:
                # Raise an error if the API is not found
                message = f"Ontology API '{search_api}' is not recognized."
                logger.info(message)
                raise ValueError(message)

    return api_instances


def run_search(ontology_data, keyword, ontology_list=None, search_api_list=None):
    """
    The master function to execute the search process. It queries the APIs, harmonizes the results, and generates a cleaned, structured response.
    
    Args:
    ontology_data (dict): Previously curated list of ontologies. Locutus_utilities - seed data
    keyword (str): The search term.
    ontology_list (List[str], optional): List of ontology names preferred by the user. Defaults to None.
    search_api_list (List[str], optional): List of API names preferred by the user or FE. Defaults to None (uses all available APIs).
    
    Returns:
    dict: The final structured response containing harmonized and curated search results.
    """
    api_instances = get_api_instance(search_api_list)

    combined_data = []
    for api_instance in api_instances:

        # Generate the search url
        search_url = api_instance.build_url(keyword, ontology_data)
        logger.info(f"URL:{search_url}")

        # Fetch the data
        api_results = api_instance.collect_data(search_url)
        logger.info(f"Count results: {len(api_results)}")

        # harmonize the api specific data into standard structure
        harmonized_data = api_instance.harmonize_data(api_results, ontology_data)
        logger.info(f"Count harmonized_data: {len(harmonized_data)}")

        # Combine the ontology api data
        combined_data.extend(harmonized_data)

    logger.info(f"Count combined_data {len(combined_data)}")

    # Final cleaning and structuring of the combined data
    response = generate_response(combined_data, search_url, ontology_list)
    logger.info(f"{keyword}")
    logger.info(response)

    return response
