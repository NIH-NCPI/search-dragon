"""
Provides the modular framework for searching across multiple ontology APIs.
"""

from search_dragon import logger as getlogger
from search_dragon.external_apis import OntologyAPI
from search_dragon.external_apis.ols_code_api import OLSSearchAPICode
from search_dragon.external_apis.ols_api import OLSSearchAPI
from search_dragon.external_apis.umls_api import UMLSSearchAPI
from search_dragon.result_structure import generate_response
from search_dragon.support import ftd_ontology_lookup
from pathlib import Path
import argparse
from rich import print
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler
import csv

SEARCH_APIS = [{"ols": OLSSearchAPI}, {"ols2": OLSSearchAPICode}, {"umls": UMLSSearchAPI}]

def get_api_instance(search_api_list):
    '''Creates instances of ontology API classes based on the provided list of APIs. If no list is provided, instances of all available APIs are created.

    Args:
    search_api_list: List of API names to initialize. Defaults to None (initialize all available APIs).
    
    Returns:
    api_instances: A list of instantiated API classes.
    '''
    logger = getlogger()
    api_instances = []

    available_apis = {key: value for api_dict in SEARCH_APIS for key, value in api_dict.items()}

    for search_api in search_api_list:
        if search_api in available_apis:
            api_instances.append(available_apis[search_api]())
        else:
            # Raise an error if the API is not found
            message = f"Ontology API '{search_api}' is not recognized."
            logger.error(message)
            raise ValueError(message)

    return api_instances



def run_search(ontology_data, keyword, ontology_list, search_api_list, results_per_page, start_index):
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
    logger = getlogger()
    api_instances = get_api_instance(search_api_list)

    combined_data = []
    for api_instance in api_instances:

        # Generate the search url
        search_url = api_instance.build_url(keyword, ontology_list, start_index, results_per_page)
        logger.debug(f"URL:{search_url}")

        # Fetch the data
        api_results, more_results_available= api_instance.collect_data(search_url, results_per_page, start_index)
        logger.debug(f"Count results: {len(api_results)}")

        # harmonize the api specific data into standard structure
        harmonized_data = api_instance.harmonize_data(api_results, ontology_data)
        logger.debug(f"Count harmonized_data: {len(harmonized_data)}")

        # Apply speciallized cleaning prior to combining data.
        cleaned_harmonized_data = api_instance.clean_harmonized_data(harmonized_data)
        
        # Combine the ontology api data
        combined_data.extend(cleaned_harmonized_data)

    logger.debug(f"Count combined_data {len(combined_data)}")

    # Final cleaning and structuring of the combined data
    response = generate_response(combined_data, search_url, more_results_available, api_instances)

    logger.debug(f"keyword: {keyword}")

    return response



def do_search(codes, ontologies, filepath, results_per_page, start_index):
    logger = getlogger()
    annotations = {}
    onto_data = ftd_ontology_lookup()

    codes = [c.strip() for c in codes.split("|")]
    ontology_param = [c.strip() for c in ontologies.split(",")]

    for keyword in codes:
        annotations[keyword]={}

        # TODO: Automate conversions.
        # Apply Ontology prefix conversions when necessary.
        ols_keyword = keyword 
        umls_keyword = keyword.replace('HP:', 'HPO:')
        if keyword.startswith('HP:'):
            ols_keyword = keyword
            umls_keyword = keyword.replace('HP:', 'HPO:')
        if keyword.startswith('HPO:'):
            ols_keyword = keyword.replace('HPO:', 'HP:')
            umls_keyword = keyword
        if keyword.startswith('OMIM:'):
            ols_keyword - keyword
            umls_keyword = keyword.replace('OMIM:', '')

        try:
            annotations[keyword]['ols'] = run_search(onto_data, ols_keyword, ontology_param, ['ols'], results_per_page, start_index)
        except:
            pass 
        try:
            annotations[keyword]['ols2'] = run_search(onto_data, ols_keyword, ontology_param, ['ols2'], results_per_page, start_index)
        except:
            pass 
        try:
            annotations[keyword]['umls'] = run_search(onto_data, umls_keyword, ontology_param, ['umls'], results_per_page, start_index)
        except:
            pass

    # Format result and output to a CSV file

    if filepath != "rich":
        fileobj = open(filepath, mode='w', newline="", encoding="utf-8")
        writer = csv.writer(fileobj)
        logger.info(f"Writing output to '{filepath}'")

        # Write header row (optional, depends on your data structure)
        writer.writerow(["api","searched_code","response_code","display","description","system","code_iri","ontology_prefix"])
    else:
        table = Table(title="Search Results", expand=True, row_styles=['yellow', 'green'])
        table.add_column("Keyword", style="magenta")
        table.add_column("Code", justify="right")
        table.add_column("Display", justify="left")
        table.add_column("system", justify="left")

    for keyword, results in annotations.items():
        for source, result in results.items():
            if result and result.get('results'):
                for entry in result['results']:
                    source = source
                    code = entry.get('code', "No results")
                    display = entry.get('display', "No results")
                    description = entry.get('description', "No results")
                    system = entry.get('system', "No results")
                    code_iri = entry.get('code_iri', "No results")
                    ontology_prefix = entry.get('ontology_prefix', "No results")
                    if filepath != "rich": 
                        writer.writerow([source, keyword, code, display, description, system, code_iri, ontology_prefix])
                    else:
                        table.add_row(keyword, code, display, system)
            else:
                if filepath != "rich":
                    writer.writerow([source, keyword, "No results", "No results", "No results", "No results", "No results", "No results"])
                else:
                    table.add_row([keyword, "No results", "No Results", ""])

    if filepath != "rich":
        fileobj.close()
    else:
        console = Console()
        console.print(table)

def exec(args=None):
    parser = argparse.ArgumentParser(description="Get metadata for a code using the available locutus OntologyAPI connection.")
    
    parser.add_argument("-ak", "--all_keywords", required=True, help="A string value containing words to search with the API. Delimeter |")
    parser.add_argument("-o", "--ontologies", required=False, default='HP,HPO,MONDO', help="A string value containing the ontology_prefixes to use in the searh")
    parser.add_argument("-f","--filepath",required=False, default='rich', help="The output filename. Path from root. (Defaults to rich tables in std out")
    parser.add_argument("-r", "--results_per_page", required=False, default=1, help="How many pages should the API return per request")
    parser.add_argument("-s", "--start_index", required=False, default = 1, help="Which page should be returned")

    args = parser.parse_args()
    
    if args.filepath == "rich":
        # For this, if we are writing to a rich table, we will write the log to a file using the default stream handler
        Path("logs").mkdir(parents=True, exist_ok=True)
        logger = getlogger("search", loglevel="DEBUG", filename="logs/search.log")
    else:
        # If we want to write the results to a file, we can configure the rich log handler to make the logging much easier to read.
        logger = getlogger("search", loglevel="DEBUG", console_handler=RichHandler(rich_tracebacks=True))

    do_search(codes=args.all_keywords,
         ontologies=args.ontologies,
         filepath=args.filepath,
         results_per_page=args.results_per_page,
         start_index=args.start_index
         )