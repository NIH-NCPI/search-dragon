import os
import requests
from search_dragon import logger

class OntologyAPI:
    def __init__(self, base_url, api_id, api_name):
        self.base_url = base_url
        self.api_id = api_id
        self.api_name = api_name

    def fetch_data(self, url):
        """ """
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None

    def remove_duplicates(self, data):
        """
        Remove duplicate records where the 'uri' field is the same.

        Args:
            data (list): List of records to filter.

        Returns:
            list: Filtered data with duplicates removed.
        """
        seen_uris = set()
        filtered_data = []
        excluded_data = []

        for item in data:
            uri = item.get("code_iri")
            if uri in seen_uris:
                excluded_data.append(item)
            else:
                seen_uris.add(uri)
                filtered_data.append(item)

        # Log the excluded records count
        message = (
            f"Records({len(excluded_data)}) were excluded as duplicates based on 'uri'.{excluded_data}"
        )
        logger.info(message)

        return filtered_data

    def remove_problem_codes(self, data):
        """
        Remove data where the data causes issues. 
        For more on special character removal, see Jira issue(s) [FD-1968] 

        Args:
            data (list): List of records to filter.

        Returns:
            list: Data without the problem causing records.
        """
        filtered_data = []
        excluded_problem_data = []
        special_characters = ["/"]

        # Remove records containing problem causing special characters
        try:
            for item in data:
                code = item.get("code")
                if any(char in code for char in special_characters):
                    excluded_problem_data.append(item)
                else:
                    filtered_data.append(item)

            # Log the excluded records count
            message = (
                f"Problem records are removed ({len(excluded_problem_data)})"
            )
            logger.info(message)

        except Exception as e:
            message = f"Error removing special character records: {e}"
            logger.error(message)
            raise Exception(message)

        return filtered_data
