"""
Ontology Lookup Service (OLS) API Integration

This script defines the `OLSSearchAPI` class that interacts with the Ontology Lookup Service (OLS) API to perform ontology searches. The class provides methods to:
- Construct search URLs with query parameters.
- Fetch paginated search results from the OLS API.
- Harmonize and structure raw results into a standardized format.

"""
from search_dragon.external_apis import OntologyAPI
from search_dragon import logger, fetch_data

OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
OLS_API = "ols"
OLS_NAME = "Ontology Lookup Service"

class OLSSearchAPI(OntologyAPI):
    def __init__(self):
        super().__init__(base_url=OLS_API_BASE_URL, api_id=OLS_API, api_name=OLS_NAME)

    def collect_data(self, search_url):
        """
        Fetch and aggregate paginated data from the provided search endpoint.

        Args:
            search_url: The base URL for the search API (e.g., "http://www.ebi.ac.uk/ols4/api/search?q=keyword").
        """
        raw_data = []
        rows=500 # Max rows allowed by the OLS
        start = 0
        total_results = None

        try:
            while total_results is None or start < total_results:
                paginated_url = f"{search_url}&rows={rows}&start={start}"
                logger.info(f"Fetching data from {paginated_url}")

                data = fetch_data(paginated_url)
                if not data:
                    logger.warning(f"No data received for start index {start}.")
                    break

                results = data.get('response', {}).get('docs', [])
                raw_data.extend(results)

                if total_results is None:
                    total_results = data.get('response', {}).get('numFound', 0)
                    logger.info(f"Total results found: {total_results}")

                logger.info(f"Retrieved {len(results)} results (start: {start}).")

                start += rows

        except Exception as e:
            logger.error(f"Error fetching data from {search_url}: {e}")
            return []

        return raw_data


    def format_keyword(self, keywords):
        """
        Formats the provided keywords for the search query.

        Args:
            keywords (str): The search terms

        Returns:
            The formatted query parameter to be inserted into the search url.
        
        Example return: "q=brain%20cancer"
        """

        keywords = keywords.replace(" ","%20")

        keyword_param=f"q={keywords}"

        return keyword_param

    def format_ontology(self, ontology_list):
        """
        Formats the included ontologies into a query parameter for the search URL.

        Args:
            ontology_list (dict): A dictionary containing ontology data.

        Returns:
            str: The formatted ontology query parameter
             
        Example return: "ontology=uberon,ma"
        """

        formatted_ontologies = ",".join(ontology_list)
        
        ontology_param =f"ontology={formatted_ontologies}"
        
        return ontology_param

    def build_url(self, keywords, ontology_list):
        """
        Constructs the search URL by combining the base URL, formatted keyword, and ontology parameters.

        Args:
            keywords (str): The search keyword(s).
            ontology_list (dict): The ontology data to be included in the search.

        Returns:
            str: The complete search URL.
        """
        url_blocks = []
        url_blocks.append(f"{self.base_url}search?")

        keyword_param = self.format_keyword(keywords)
        ontology_param = self.format_ontology(ontology_list)

        # Join the query params with & then join the params to the base url
        url_blocks.append("&".join([keyword_param,ontology_param]))
        complete_url = "".join(url_blocks)

        return complete_url
    
    def harmonize_data(self, raw_results, ontology_data):
        """
        Harmonizes the raw API results into a standardized format for further processing.

        Args:
            raw_results (dict or list): Raw results returned from the OLS API.
            ontology_data (dict): The ontology data used to get ontology systems

        Returns:
            dict: A dictionary containing the harmonized data.
        """
        if isinstance(raw_results, list):
            return [self.harmonize_data(item, ontology_data) for item in raw_results]

        # Get the ontology prefix from the raw result
        ontology_prefix = raw_results.get("ontology_prefix")

        # Retrieve the corresponding value from ontology_list
        system = ontology_data.get(ontology_prefix)

        harmonized_data = {
            "code": raw_results.get("obo_id"),
            "system": system,
            "code_iri": raw_results.get("iri"),
            "display": raw_results.get("label"),
            "description": raw_results.get("description", []),
            "ontology_prefix": ontology_prefix,
        }

        return harmonized_data