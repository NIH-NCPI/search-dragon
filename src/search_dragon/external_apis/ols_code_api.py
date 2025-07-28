"""
Ontology Lookup Service (OLS) API Integration

This url is more reliable for searching on a code(HP:0003045)

https://www.ebi.ac.uk/ols4/api/v2/entities?search=HP%3A0003045&page=2size=10

This script defines the `OLSSearchAPI` class that interacts with the Ontology Lookup Service (OLS) API to perform ontology searches. The class provides methods to:
- Construct search URLs with query parameters.
- Fetch paginated search results from the OLS API.
- Harmonize and structure raw results into a standardized format.

"""
from search_dragon.external_apis import OntologyAPI
from search_dragon import logger

class OLSSearchAPICode(OntologyAPI):
    def __init__(self):
        super().__init__(
            base_url="https://www.ebi.ac.uk/ols4/api/v2/entities",
            api_id="ols2",
            api_name="Ontology Lookup Service V2",
        )
        self.total_results_id = 'totalElements'

    def collect_data(self, search_url, results_per_page, start_index):
        """
        Fetch a single page of data from the provided search endpoint.

        Args:
            search_url: The base URL for the search API.
            results_per_page: Number of results to fetch in this request (max allowed: 500).
            row_start: The starting row index for fetching data.

        Returns:
            Tuple:
                - raw_data (list): Results from the requested page.
                - more_results_available (bool): Whether more results are available.
        """
        raw_data = []
        results_per_page = int(results_per_page)
        start_index = int(start_index)
        total_results = 0
        more_results_available = False

        if results_per_page > 500:
            logger.info(
                f"Max rows allowed by OLS is 500. results_per_page: {results_per_page} could be causing an issue."
            )

        try:
            paginated_url = f"{search_url}&size={results_per_page}&page={start_index}"
            logger.info(f"Fetching data from {paginated_url}")

            data = self.fetch_data(paginated_url)
            # import pdb
            # pdb.set_trace()
            results = data.get("elements", [])
            raw_data.extend(results)

            total_results = data.get(self.total_results_id, 0)
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
        
        """
        keywords = keywords.replace(" ","%20")
        keywords = keywords.replace(":","%3A")

        keyword_param=f"search={keywords}"

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

    def format_results_per_page(self, results_per_page):
        """
        Formats the results_per_page into a format readable by the api.
        """
        page_size_param = f"size={results_per_page}"

        return page_size_param

    def format_start_index(self, start_index):
        """
        Formats the start_index into a format readable by the api.
        """
        start_param = f"page={start_index}"

        return start_param


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
        # ontology_param = self.format_ontology(ontology_list)
        start_param = self.format_start_index(start_index)
        page_size_param = self.format_results_per_page(results_per_page)

        # Join the query params with & then join the params to the base url
        url_blocks.append(
            "&".join(
                [
                    keyword_param,
                    # ontology_param,
                    start_param,
                    page_size_param,
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

        # import pdb
        # pdb.set_trace()

        # Get the ontology prefix from the raw result
        ontology_prefix = raw_results.get("definedBy") or "ERR:CURIE" # ERRs are caught by validate_data and not returned

        # Retrieve the corresponding value from ontology_list
        system = ontology_data.get(ontology_prefix[0].upper()) or "ERR:SYSTEM" # ERRs are caught by validate_data and not returned

        display = raw_results.get("label")[0]

        harmonized_data = {
            "code": raw_results.get("curie"),
            "system": system,
            "code_iri": raw_results.get("iri"),
            "display": display,
            "description": display,
            "ontology_prefix": ontology_prefix[0].upper(),
        }

        return harmonized_data

    def clean_harmonized_data(self, data):
        """
        Cleans the harmonized data to the specifications required for this API.

        Cleans using the functions defined in the base class unless overwritten
        in the API subclass.
        """
        cleaned_data = self.remove_duplicates(data)

        return cleaned_data
