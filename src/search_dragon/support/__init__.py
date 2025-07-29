import importlib_resources

from csv import DictReader 

_support_details = (
    importlib_resources.files("search_dragon") / "support"
) 

def ftd_ontology_lookup(csv_path=None):
    if csv_path is None:
        csv_path = _support_details / "ftd_ontology_lookup.csv"
    
    with open(csv_path, 'rt') as infile:
        onto_data = {}

        lkup = DictReader(infile, delimiter=',', quotechar='"')
        for row in lkup:
            onto_data[row['curie']] = row['system']

    return onto_data

    