from search_dragon import logger, fetch_data

class OntologyAPI:
    def __init__(self, base_url, api_id, api_name):
        self.base_url = base_url
        self.api_id = api_id
        self.api_name = api_name

        
    def collect_data(self, search_url):
        """
        """
        raw_data = []

        logger.info(f"Fetching data from {search_url}")
        try:
            data = fetch_data(search_url)
            while '_links' in data and 'next' in data['_links']:
                raw_data.extend(data.get('response', {}).get('docs', []))
                next_url = data['_links']['next']['href']
                logger.info(f"Fetching next page: {next_url}")
                data = fetch_data(next_url)
                if not data:
                    break

            # Add the data from the last page
            raw_data.extend(data.get('response', {}).get('docs', []))

        except Exception as e:
            logger.error(f"Error fetching data from {search_url}: {e}")
            return []

        return raw_data
            

