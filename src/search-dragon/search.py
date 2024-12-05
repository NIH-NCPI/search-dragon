"""
Run api requests in parallel?

What info needs to come from front end(optional/required)
    Search - keyword - required single string at this point(list later for fuzzy matches)
    Filter - ontology(s) - optional - list
    Fuzzy search as option? - future addition - optional
"""

from common import SEARCH_API_BASE_URLS, LOGS_PATH
from utils import set_logging_config
from search import OntologyAPI
import requests
import logging
import datetime
import argparse


def fetch_data(url):
    """
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def transform_data(raw_data, api_instance):
    """
    Harmonize data
    """
    transformed_data = []
    for item in raw_data:
        transformed_data.append()
    return transformed_data

def collect_data(search_url, api_instance):
    """
    """
    all_raw_data = []

    logging.info(f"Fetching data from {search_url}")
    data = fetch_data(search_url)

    while '_links' in data and 'next' in data['_links']:
        all_raw_data.extend(data.get('items', [])) 
        next_url = data['_links']['next']['href']
        logging.info(f"Fetching next page: {next_url}")
        data = fetch_data(next_url)
        if not data:
            break

    all_raw_data.extend(data.get('items', []))
        
    logging.info(f"Harmonizing collected data...")
    transformed_data = transform_data(all_raw_data, api_instance)
    
    logging.info(f"Data collection complete. {len(transformed_data)} items transformed.")
    return transformed_data


def run_search(keyword):
    """
    The master function
    
    """
    _log_file = f"{LOGS_PATH}{datetime.now().strftime('%Y%m%d_%H%M%S')}_search.log"
    set_logging_config(log_file = _log_file)


    # Collect and harmonize ontology api search results
    # Run in parallel?
    search_data = []
    for search_api in SEARCH_API_BASE_URLS:
        # Instantiate the search api
        api_instance = OntologyAPI.get_api_instance(search_api)

        # Generate search urls
        search_url = api_instance.build_url(keyword)

        api_results = collect_data(search_url, api_instance)

        # General filtering/formatting stage each api response (filter.py)
        # API specific cleaning done in the collect_data transformation/harmonization stage (collect_data())

        search_api.append(api_results)

    # Generate response - counts and general formatting (response_structure.py)

    return search_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modular API Ontology Search")
    parser.add_argument('-k', '--keyword', required=True, help="keyword to search")
    parser.add_argument('-o', '--ontologies', required=True, help="User preferred Ontologies")

    args = parser.parse_args()

    run_search(keyword=args.keyword)
