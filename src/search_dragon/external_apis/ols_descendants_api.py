import urllib.parse

import rich

from search_dragon import logger as getlogger
from search_dragon.external_apis.ols_code_api import OLSSearchAPICode


class OLSDescendantsAPI(OLSSearchAPICode):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ebi.ac.uk/ols4/api/ontologies"
        self.api_id = "olsd"
        self.api_name = "Ontology Lookup Service"
        self.total_results_id = "totalElements"

    def collect_data(self, search_url, results_per_page, start_index):
        # results_per_page and start_index are not used in this class, but kept since they are used in other classes
        """
        Fetch all pages of data from the provided search endpoint.

        Args:
            search_url: The base URL for the search API.

        Returns:
            Tuple:
                - raw_data (list): Results from the requested page.
        """
        logger = getlogger()
        raw_data = []

        try:
            current_page = 0
            while True:
                paginated_url = f"{search_url}?page={current_page}"

                data = self.fetch_data(paginated_url)
                results = data.get("_embedded", {}).get("terms", [])
                raw_data.extend(results)

                page_obj = data.get("page", {})
                total_pages = page_obj.get("totalPages", 1)
                total_elements = page_obj.get("totalElements", 0)
                logger.debug(
                    f"Page {current_page + 1} of {total_pages}. Total elements: {total_elements}"
                )

                current_page += 1
                if current_page >= total_pages:
                    break

        except Exception as e:
            logger.error(f"Error fetching data from {search_url}: {e}")
            return [], False

        return raw_data, False

    def format_iri(self, iri):
        """
        Formats the provided iri for the search query.

        Args:
            iri (str): The code iri

        Returns:
            The formatted iri parameter to be inserted into the search url.

        """
        # Safe, robust double-encoding
        double_encoded_iri = urllib.parse.quote(
            urllib.parse.quote(iri, safe=""), safe=""
        )

        return double_encoded_iri

    def build_url(
        self,
        keywords,
        ontology_list,
        start_index,
        results_per_page,
        iri=None,
        children=False,
    ):
        # TODO: add direct only args above. If direct only arg is there, do conditional below to use the children query instead (look into this to make sure that's correct)
        # results_per_page and start_index are not used in this class, but kept since they are used in other classes
        """
        Constructs the search URL by combining the base URL, formatted keyword, and ontology parameters.

        Args:
            ontology_list (dict): The ontology data to be included in the search.
            iri (str): The formatted iri in the URL query

        Returns:
            str: The complete search URL.
        """
        url_blocks = []
        url_blocks.append(f"{self.base_url}/")

        iri_param = self.format_iri(iri)

        last_term = "children" if children else "descendants"

        # Join the query params with / then join the params to the base url
        url_blocks.append("/".join([ontology_list, "terms", iri_param, last_term]))
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
        ontology_prefix = raw_results.get(
            "ontology_prefix", "ERR:CURIE"
        )  # ERRs are caught by validate_data and not returned

        # Retrieve the corresponding value from ontology_list
        system = ontology_data.get(
            ontology_prefix.upper() or "ERR:SYSTEM"
        )  # ERRs are caught by validate_data and not returned

        display = raw_results.get("label")
        harmonized_data = {
            "code": raw_results.get("obo_id"),
            "system": system,
            "code_iri": raw_results.get("iri"),
            "display": display,
            "description": display,
            "ontology_prefix": ontology_prefix.upper(),
        }

        return harmonized_data
