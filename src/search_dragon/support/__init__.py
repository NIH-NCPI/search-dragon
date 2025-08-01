from importlib import resources as importlib_resources
from search_dragon import logger
from csv import DictReader 

_support_details = importlib_resources.files("search_dragon") / "support"

def ftd_ontology_lookup(csv_path=None):
    """Return the lookup as a dictionary: curie=>system"""
    if csv_path is None:
        csv_path = _support_details / "ftd_ontology_lookup.csv"

    onto_data = {}
    try:
        with importlib_resources.as_file(csv_path) as path:
            with open(path, 'rt') as infile:
                lkup = DictReader(infile, delimiter=',', quotechar='"')
                for row in lkup:
                    onto_data[row['curie']] = row['system']
    except Exception as e:
        logger().error(f"An error was encountered when loading FTD Ontological Lookup data: {e}")

    return onto_data
    