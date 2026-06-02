import json

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
        """
        Fetch a single page of data from the provided search endpoint.

        Args:
            search_url: The base URL for the search API.
            results_per_page: Number of results to fetch in this request (max allowed: 1000).

        Returns:
            Tuple:
                - raw_data (list): Results from the requested page.
                - more_results_available (bool): Whether more results are available.
        """
        logger = getlogger()
        raw_data = []
        results_per_page = int(results_per_page)
        total_results = 0
        more_results_available = False

        if results_per_page > 1000:
            logger.debug(
                f"Max rows allowed by OLS is 1000. results_per_page: {results_per_page} could be causing an issue."
            )

        try:
            # paginated_url = f"{search_url}&size={results_per_page}&page={start_index}"
            paginated_url = f"{search_url}"

            logger.debug(f"Fetching data from {paginated_url}")

            data = self.fetch_data(paginated_url)
            # print(json.dumps(data, indent=2))
            # import pdb

            # pdb.set_trace()
            results = data.get("_embedded", {}).get("terms", [])

            raw_data.extend(results)

            total_results = data.get("page", {}).get("totalElements", 0)
            logger.debug(f"Total results found: {total_results}")
            logger.debug(
                f"Retrieved {len(results)} results (start_index: {start_index})."
            )

            # Check if the start_index exceeds total results
            if start_index > total_results:
                message = f"start_index ({start_index}) exceeds total available results ({total_results})."
                logger.error(message)
                raise ValueError(message)

            # Check if more results are available after this request.
            n_results_used = start_index + results_per_page + 1
            more_results_available = n_results_used < total_results

        except Exception as e:
            logger.error(f"Error fetching data from {clean_url(search_url)}: {e}")
            return [], more_results_available

        return raw_data, more_results_available

    def format_iri(self, iri):
        """
        Formats the provided iri for the search query.

        Args:
            iri (str): The code iri

        Returns:
            The formatted iri parameter to be inserted into the search url.

        """
        iri = iri.replace(":", "%253A")
        iri = iri.replace("/", "%252F")

        return iri

    def build_url(
        self, keywords, ontology_list, start_index, results_per_page, iri=None
    ):
        """
        Constructs the search URL by combining the base URL, formatted keyword, and ontology parameters.

        Args:
            keywords (str): The search keyword(s).
            ontology_list (dict): The ontology data to be included in the search.

        Returns:
            str: The complete search URL.
        """
        url_blocks = []
        url_blocks.append(f"{self.base_url}/")

        iri_param = self.format_iri(iri)
        # ontology_param = self.format_ontology(ontology_list)
        # start_param = self.format_start_index(start_index)
        # page_size_param = self.format_results_per_page(results_per_page)

        # Join the query params with & then join the params to the base url
        url_blocks.append(
            "/".join(
                [
                    ontology_list,
                    "terms",
                    iri_param,
                    "descendants",
                ]
            )
        )
        complete_url = "".join(url_blocks)
        # print(f"THIS IS THE URL: {complete_url}")

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
        ontology_prefix = (
            raw_results.get("ontology_prefix") or "ERR:CURIE"
        )  # ERRs are caught by validate_data and not returned

        # Retrieve the corresponding value from ontology_list
        system = ontology_data.get(
            ontology_prefix.upper() or "ERR:SYSTEM"
        )  # ERRs are caught by validate_data and not returned
        print(f"SYSTEM: {ontology_data.get(ontology_prefix)}")

        display = raw_results.get("label")

        harmonized_data = {
            "code": raw_results.get("obo_id"),
            "system": system,
            "code_iri": raw_results.get("iri"),
            "display": display,
            "description": display,
            "ontology_prefix": ontology_prefix[0].upper(),
        }

        return harmonized_data
