"""
Run api requests in parallel?

What info needs to come from front end(optional/required)
    Search - keyword - required single string at this point(list later for fuzzy matches)
    Filter - ontology(s) - optional - list
    Fuzzy search as option? - future addition - optional
"""

from search_dragon import logger
from search_dragon.sources import OntologyAPI
from search_dragon.sources.ols_api import OLSSearchAPI
from search_dragon.result_structure import generate_response
from search_dragon.curate_combined_data import curate_combined_data
import argparse

SEARCH_APIS = ["ols"]

def get_api_instance(search_api):

    if search_api == "ols" or search_api == "all":
        return OLSSearchAPI()
    else:
        message = f"Ontology API: {search_api} is not recognized."
        logger.info(message)
        raise ValueError(message)


def run_search(search_api_list, keyword, ontology_list):
    """
    The master function

    """
    # Collect and harmonize ontology api search results
    # Run in parallel? threads mutex
    # send to yelena as the results come in? Yelena send multiple calls instead. - new arg api to run
    # We really want this.
    # If FE calls each api request separately. How to harmonize the data? ie duplicates.
    api_instances=[]
    for api in search_api_list:
        api_instances.append(get_api_instance(api))

    combined_data = []
    for api_instance in api_instances:

        # Generate the search url
        search_url = api_instance.build_url(keyword)
        logger.info(f"URL:{search_url}")

        # Fetch the data
        api_results = api_instance.collect_data(search_url)
        logger.info(f"Count results: {len(api_results)}")

        # harmonize the api specific data into standard structure
        harmonized_data = api_instance.harmonize_data(api_results)
        logger.info(f"Count harmonized_data: {len(harmonized_data)}")

        # Combine the ontology api data
        combined_data.extend(harmonized_data)

    logger.info(f"Count combined_data {len(combined_data)}")
    # general cleaning and validation of the combined data. Not API specific
    curated_data = curate_combined_data(combined_data, ontology_list)

    # Final cleaning and structuring of the combined data
    response = generate_response(curated_data)
    logger.info(f"{keyword}")
    logger.info(f"response:{response}")

    return response


def main():
    parser = argparse.ArgumentParser(description="Modular API Ontology Search")
    parser.add_argument(
        "-s",
        "--search_api",
        required=False,
        default=["all"],
        nargs="*",
        help=(
            "Specify one or more APIs to use for ontology data retrieval. "
            "Available options:\n"
            "  'ols': Gather data with the Ontology Lookup Service API."
            "  'all': Gather data using all available ontology APIs."
        ),
    )
    parser.add_argument(
        "-k",
        "--keywords",
        required=False,
        default=["Bartonella henselae"],
        nargs="*",
        help="keyword(s) to search",
    )
    parser.add_argument(
        "-o", "--ontologies",
        required=False,
        default=[None],
        nargs="*",
        help="User preferred Ontologies"
    )

    args = parser.parse_args()

    run_search(
        search_api_list=args.search_api,
        keyword=args.keywords,
        ontology_list=args.ontologies,
    )


if __name__ == "__main__":
    main()
