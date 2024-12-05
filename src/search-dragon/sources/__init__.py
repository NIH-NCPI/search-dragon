class OntologyAPI:
    def __init__(self, base_url, api_id, api_name):
        self.base_url = base_url
        self.api_id = api_id
        self.api_name = api_name

    def get_api_instance(search_api):
        if search_api == "ols":
            return OLSSearchAPI()
        else:
            pass

    # make collect_data a member function