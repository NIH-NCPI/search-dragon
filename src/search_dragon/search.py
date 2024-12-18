"""
Run api requests in parallel?

What info needs to come from front end(optional/required)
    Search - keyword - required single string at this point(list later for fuzzy matches)
    Filter - ontology(s) - optional - list
    Fuzzy search as option? - future addition - optional
"""

from search_dragon import logger
from search_dragon.external_apis import OntologyAPI
from search_dragon.external_apis.ols_api import OLSSearchAPI
from search_dragon.result_structure import generate_response
from search_dragon.curate_combined_data import curate_combined_data
import argparse

SEARCH_APIS = [{"ols": OLSSearchAPI}]


def get_api_instance(search_api_list=None):
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
    The master function

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
    # general cleaning and validation of the combined data. Not API specific
    curated_data = curate_combined_data(combined_data, ontology_list)

    # Final cleaning and structuring of the combined data
    response = generate_response(curated_data, search_url)
    logger.info(f"{keyword}")
    logger.info(response)

    return response
