from importlib import resources as importlib_resources
from search_dragon import logger

from csv import DictReader 

_support_details = (
    importlib_resources.files("search_dragon") / "support"
) 

def ftd_ontology_lookup(csv_path=None):
    if csv_path is None:
        csv_path = _support_details / "ftd_ontology_lookup.csv"

    try:    
        with open(csv_path, 'rt') as infile:
            onto_data = {}

            lkup = DictReader(infile, delimiter=',', quotechar='"')
            for row in lkup:
                onto_data[row['curie']] = row['system']
    except Exception as e:
        logger().error(f"An error was encountered when loading FTD Ontological Lookup data: {e}")

    return onto_data

    