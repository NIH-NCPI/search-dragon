"""
UMLS (Unified Medical Language System) API Integration

This script defines the `UMLSSearchAPI` class that interacts with the umls API to perform ontology searches. The class provides methods to:
- Construct search URLs with query parameters.
- Fetch paginated search results from the UMLS API.
- Harmonize and structure raw results into a standardized format.

"""

from search_dragon.external_apis import OntologyAPI
from search_dragon import logger
import os

class UMLSSearchAPI(OntologyAPI):
    def __init__(self):
        super().__init__(
            base_url="https://uts-ws.nlm.nih.gov/rest/search/current",
            api_id= "umls",
            api_name="Unified Medical Language System",
        )
        self.total_results_id='recCount'

    def collect_data(self, search_url, results_per_page, start_index):
        """
        Fetch a single page of data from the provided search endpoint.

        Args:
            search_url (str): The base URL for the search API.
            results_per_page (int): Number of results to fetch in this request.
            start_index (int): The starting page number for fetching data.

        Returns:
            Tuple:
                - raw_data (list): Results from the requested page.
                - more_results_available (bool): Whether more results are available.
        """
        raw_data = []
        results_per_page = int(results_per_page)
        start_index = int(start_index)
        more_results_available = False

        try:
            # Construct the paginated URL
            paginated_url = f"{search_url}"
            logger.info(f"Fetching data from {paginated_url}")

            # Fetch data
            data = self.fetch_data(paginated_url)
            logger.info(f"Returned data: {data}")

            # Extract results
            results = data.get("result", {}).get("results", [])
            raw_data.extend(results)
            
            total_results = data.get("result", {}).get(self.total_results_id, 0)
            logger.info(f"Total results found: {total_results}")
            logger.info(f"Retrieved {len(results)} results (start_index: {start_index}).")

            # Check if the start_index exceeds total results
            if start_index >= total_results:
                message = f"start_index ({start_index}) exceeds total available results ({total_results})."
                logger.error(message)
                raise ValueError(message)

            # Check if more results are available after this request.
            n_results_used = start_index + results_per_page + 1
            more_results_available = n_results_used < total_results

        except Exception as e:
            logger.error(f"Error fetching data from {search_url}: {e}")
            return [], more_results_available

        return raw_data, more_results_available

    def format_keyword(self, keywords):
        """
        Formats the provided keywords for the search query.

        Args:
            keywords (str): The search terms

        Returns:
            The formatted query parameter to be inserted into the search url.

        Example return: "q=brain%20cancer"
        """

        keywords = keywords.replace(" ", "%20")

        keyword_param = f"string={keywords}"

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

        ontology_param = f"sabs={formatted_ontologies}"

        return ontology_param
    
    def get_api_key(self):
        API_KEY = os.getenv("UMLS_API_KEY")
        if not API_KEY:
            raise ValueError(
                f"API_KEY for 'umls' is not set in the environment variables."
            )
        else:
            return API_KEY
        
    def format_key(self):
        """
        Formats the api key into a format readable by the api.
        """
        api_key = self.get_api_key()
        key_param = f"apiKey={api_key}"

        return key_param

    def format_results_per_page(self, results_per_page):
        """
        Formats the results_per_page into a format readable by the api.
        """
        page_size_param = f"pageSize={results_per_page}"

        return page_size_param

    def format_start_index(self, start_index):
        """
        Formats the start_index into a format readable by the api.
        """
        start_param = f"pageNumber={start_index}"

        return start_param

    def format_api_specific_params(self):
        """
        Formats the parameters that aren't required across all apis
        """
        return_type_param = f"returnIdType=code"

        return return_type_param

    def build_url(self, keywords, ontology_list, start_index, results_per_page):
        """
        Constructs the search URL by combining the base URL, formatted keyword, and ontology parameters.

        Args:
            keywords (str): The search keyword(s).
            ontology_list (dict): The ontology data to be included in the search.

        Returns:
            str: The complete search URL.
        """
        url_blocks = []
        url_blocks.append(f"{self.base_url}?")

        keyword_param = self.format_keyword(keywords)
        ontology_param = self.format_ontology(ontology_list)
        start_param = self.format_start_index(start_index)
        page_size_param = self.format_results_per_page(results_per_page)
        return_type_param = self.format_api_specific_params()

        key_param = self.format_key()

        # Join the query params with & then join the params to the base url
        url_blocks.append(
            "&".join(
                [
                    keyword_param,
                    ontology_param,
                    start_param,
                    page_size_param,
                    return_type_param,
                    key_param,
                ]
            )
        )
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
        ontology_prefix = raw_results.get("rootSource")

        # Retrieve the corresponding value from ontology_list
        system = ontology_data.get(ontology_prefix)

        harmonized_data = {
            "code": raw_results.get(
                "ui", ""
            ),  # The umls Concept Unique Identifier (CUI)
            "system": system,  # This is the ontology system.
            "code_iri": raw_results.get("uri"),
            "display": raw_results.get("name"),
            "description": raw_results.get("name", []),
            "ontology_prefix": ontology_prefix,
        }

        return harmonized_data
