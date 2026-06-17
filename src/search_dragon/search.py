"""
Provides the modular framework for searching across multiple ontology APIs.
"""

import argparse
import csv
from pathlib import Path

from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from search_dragon import logger as getlogger
from search_dragon.external_apis import OntologyAPI
from search_dragon.external_apis.ols_api import OLSSearchAPI
from search_dragon.external_apis.ols_code_api import OLSSearchAPICode
from search_dragon.external_apis.ols_descendants_api import OLSDescendantsAPI
from search_dragon.external_apis.umls_api import UMLSSearchAPI
from search_dragon.result_structure import clean_url, generate_response
from search_dragon.support import ftd_ontology_lookup

SEARCH_APIS = [
    {"ols": OLSSearchAPI},
    {"ols2": OLSSearchAPICode},
    {"olsd": OLSDescendantsAPI},
    {"umls": UMLSSearchAPI},
]


def get_api_instance(search_api_list):
    """Creates instances of ontology API classes based on the provided list of APIs. If no list is provided, instances of all available APIs are created.

    Args:
    search_api_list: List of API names to initialize. Defaults to None (initialize all available APIs).

    Returns:
    api_instances: A list of instantiated API classes.
    """
    logger = getlogger()
    api_instances = []

    available_apis = {
        key: value for api_dict in SEARCH_APIS for key, value in api_dict.items()
    }

    for search_api in search_api_list:
        if search_api in available_apis:
            api_instances.append(available_apis[search_api]())
        else:
            # Raise an error if the API is not found
            message = f"Ontology API '{search_api}' is not recognized."
            logger.error(message)
            raise ValueError(message)

    return api_instances


def run_search(
    ontology_data,
    keyword,
    ontology_list,
    search_api_list,
    results_per_page,
    start_index,
    iri=None,
    descendants=False,
    children=False,
):
    """
    The master function to execute the search process. It queries the APIs, harmonizes the results, and generates a cleaned, structured response.

    Args:
    ontology_data (dict): Previously curated list of ontologies. Locutus_utilities - seed data
    keyword (str): The search term.
    ontology_list (List[str], optional): List of ontology names preferred by the user. Defaults to None.
    search_api_list (List[str], optional): List of API names preferred by the user or FE. Defaults to None (uses all available APIs).

    Returns:
    dict: The final structured response containing harmonized and curated search results.
    """

    logger = getlogger()
    api_instances = get_api_instance(search_api_list)

    combined_data = []
    for api_instance in api_instances:
        # Generate the search url
        search_url = api_instance.build_url(
            keyword,
            ontology_list,
            start_index,
            results_per_page,
            iri,
            children=children,
        )
        logger.debug(f"URL:{clean_url(search_url)}")

        # Fetch the data
        api_results, more_results_available = api_instance.collect_data(
            search_url, results_per_page, start_index
        )
        logger.debug(f"Count results: {len(api_results)}")

        # harmonize the api specific data into standard structure
        harmonized_data = api_instance.harmonize_data(api_results, ontology_data)

        logger.debug(f"Count harmonized_data: {len(harmonized_data)}")

        # Apply speciallized cleaning prior to combining data.
        cleaned_harmonized_data = api_instance.clean_harmonized_data(harmonized_data)

        # Combine the ontology api data
        combined_data.extend(cleaned_harmonized_data)

    logger.debug(f"Count combined_data {len(combined_data)}")

    # Final cleaning and structuring of the combined data
    response = generate_response(
        combined_data, search_url, more_results_available, api_instances, descendants
    )

    logger.debug(f"keyword: {keyword}")

    return response


def do_search(codes, ontologies, filepath, results_per_page, start_index):
    logger = getlogger()
    annotations = {}
    onto_data = ftd_ontology_lookup()

    codes = [c.strip() for c in codes.split("|")]
    ontology_param = [c.strip() for c in ontologies.split(",")]

    for keyword in codes:
        annotations[keyword] = {}

        # TODO: Automate conversions.
        # Apply Ontology prefix conversions when necessary.
        ols_keyword = keyword
        umls_keyword = keyword.replace("HP:", "HPO:")
        if keyword.startswith("HP:"):
            ols_keyword = keyword
            umls_keyword = keyword.replace("HP:", "HPO:")
        if keyword.startswith("HPO:"):
            ols_keyword = keyword.replace("HPO:", "HP:")
            umls_keyword = keyword
        if keyword.startswith("OMIM:"):
            ols_keyword = keyword
            umls_keyword = keyword.replace("OMIM:", "")
        if keyword.startswith("SNOMEDCT:"):
            ols_keyword = keyword.replace("SNOMEDCT:", "SNOMED:")
            umls_keyword = keyword

        try:
            annotations[keyword]["ols"] = run_search(
                onto_data,
                ols_keyword,
                ontology_param,
                ["ols"],
                results_per_page,
                start_index,
            )
        except:
            pass
        try:
            annotations[keyword]["ols2"] = run_search(
                onto_data,
                ols_keyword,
                ontology_param,
                ["ols2"],
                results_per_page,
                start_index,
            )
        except:
            pass
        try:
            annotations[keyword]["umls"] = run_search(
                onto_data,
                umls_keyword,
                ontology_param,
                ["umls"],
                results_per_page,
                start_index,
            )
        except:
            pass

    # Format result and output to a CSV file

    if filepath != "rich":
        fileobj = open(filepath, mode="w", newline="", encoding="utf-8")
        writer = csv.writer(fileobj)
        logger.info(f"Writing output to '{filepath}'")

        # Write header row (optional, depends on your data structure)
        writer.writerow(
            [
                "api",
                "searched_code",
                "response_code",
                "display",
                "description",
                "system",
                "code_iri",
                "ontology_prefix",
            ]
        )
    else:
        table = Table(
            title="Search Results", expand=True, row_styles=["yellow", "green"]
        )
        table.add_column("Keyword", style="magenta")
        table.add_column("Code", justify="right")
        table.add_column("Display", justify="left")
        table.add_column("system", justify="left")

    for keyword, results in annotations.items():
        for source, result in results.items():
            if result and result.get("results"):
                for entry in result["results"]:
                    source = source
                    code = entry.get("code", "No results")
                    display = entry.get("display", "No results")
                    description = entry.get("description", "No results")
                    system = entry.get("system", "No results")
                    code_iri = entry.get("code_iri", "No results")
                    ontology_prefix = entry.get("ontology_prefix", "No results")
                    if filepath != "rich":
                        writer.writerow(
                            [
                                source,
                                keyword,
                                code,
                                display,
                                description,
                                system,
                                code_iri,
                                ontology_prefix,
                            ]
                        )
                    else:
                        table.add_row(keyword, code, display, system)
            else:
                if filepath != "rich":
                    writer.writerow(
                        [
                            source,
                            keyword,
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                        ]
                    )
                else:
                    table.add_row(keyword, "No results", "No Results", "")

    if filepath != "rich":
        fileobj.close()
    else:
        console = Console()
        console.print(table)


def desc_search(
    codes,
    ontologies,
    filepath,
    results_per_page,
    start_index,
    iri,
    parent_data,
    children,
):
    codes = [codes] if codes else [iri.split("/")[-1].replace("_", ":")]
    logger = getlogger()
    annotations = {}
    onto_data = ftd_ontology_lookup()
    for parent_code in codes:
        annotations[parent_code] = {}

        # TODO: Automate conversions.
        # Apply Ontology prefix conversions when necessary.
        ols_keyword = parent_code
        umls_keyword = parent_code.replace("HP:", "HPO:")
        if parent_code.startswith("HP:"):
            ols_keyword = parent_code
            umls_keyword = parent_code.replace("HP:", "HPO:")
        if parent_code.startswith("HPO:"):
            ols_keyword = parent_code.replace("HPO:", "HP:")
            umls_keyword = parent_code
        if parent_code.startswith("OMIM:"):
            ols_keyword = parent_code
            umls_keyword = parent_code.replace("OMIM:", "")
        if parent_code.startswith("SNOMEDCT:"):
            ols_keyword = parent_code.replace("SNOMEDCT:", "SNOMED:")
            umls_keyword = parent_code

        try:
            annotations[parent_code]["olsd"] = run_search(
                onto_data,
                ols_keyword,
                ontologies,
                ["olsd"],
                results_per_page,
                start_index,
                iri,
                descendants=True,
                children=children,
            )
        except:
            pass

    # Format result and output to a CSV file

    if filepath != "rich":
        fileobj = open(filepath, mode="w", newline="", encoding="utf-8")
        writer = csv.writer(fileobj)
        logger.info(f"Writing output to '{filepath}'")

        # Write header row (optional, depends on your data structure)
        writer.writerow(
            [
                "api",
                "parent_code",
                "descendant_code",
                "display",
                "description",
                "system",
                "code_iri",
                "ontology_prefix",
            ]
        )

        if parent_data:
            description = parent_data.get("description", "")
            if isinstance(description, list):
                description = "\n".join(description)
            writer.writerow(
                [
                    "ols2",
                    "",
                    parent_data.get("code"),
                    parent_data.get("display", ""),
                    description,
                    parent_data.get("system", ""),
                    parent_data.get("code_iri", ""),
                    parent_data.get("ontology_prefix", ""),
                ]
            )
    else:
        table = Table(
            title="Search Results", expand=True, row_styles=["yellow", "green"]
        )
        table.add_column("Parent Code", style="magenta")
        table.add_column("Code", justify="right")
        table.add_column("Display", justify="left")
        table.add_column("system", justify="left")

    for parent_code, results in annotations.items():
        for source, result in results.items():
            if result and result.get("results"):
                for entry in result["results"]:
                    source = source
                    code = entry.get("code", "No results")
                    display = entry.get("display", "No results")
                    description = entry.get("description", "No results")
                    system = entry.get("system", "No results")
                    code_iri = entry.get("code_iri", "No results")
                    ontology_prefix = entry.get("ontology_prefix", "No results")
                    if filepath != "rich":
                        writer.writerow(
                            [
                                source,
                                parent_code,
                                code,
                                display,
                                description,
                                system,
                                code_iri,
                                ontology_prefix,
                            ]
                        )
                    else:
                        table.add_row(parent_code, code, display, system)
            else:
                if filepath != "rich":
                    writer.writerow(
                        [
                            source,
                            parent_code,
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                            "No results",
                        ]
                    )
                else:
                    table.add_row(parent_code, "No results", "No Results", "")

    if filepath != "rich":
        fileobj.close()
    else:
        console = Console()
        console.print(table)


def exec(args=None):
    parser = argparse.ArgumentParser(
        description="Get metadata for a code using the available locutus OntologyAPI connection."
    )

    parser.add_argument(
        "-ak",
        "--all_keywords",
        required=False,
        help="A string value containing words to search with the API. Delimeter |. This argument is required when -d/--descendants argument is not used",
    )
    parser.add_argument(
        "-o",
        "--ontologies",
        required=False,
        default=None,
        help="A string value containing the ontology_prefixes to use in the searh",
    )
    parser.add_argument(
        "-f",
        "--filepath",
        required=False,
        default="rich",
        help="The output filename. Path from root. (Defaults to rich tables in std out",
    )
    parser.add_argument(
        "-r",
        "--results_per_page",
        required=False,
        default=1,
        help="How many pages should the API return per request",
    )
    parser.add_argument(
        "-s",
        "--start_index",
        required=False,
        default=1,
        help="Which page should be returned",
    )
    parser.add_argument(
        "-d",
        "--descendants",
        required=False,
        action="store_true",
        help="Pull all descendants for a given code",
    )
    parser.add_argument(
        "-i",
        "--iri",
        required=False,
        default=None,
        type=str,
        help="The iri for the parent code to pull descendants",
    )
    parser.add_argument(
        "-p",
        "--parent_data",
        required=False,
        action="store_true",
        default=None,
        help="Include details of the parent node",
    )
    parser.add_argument(
        "-c",
        "--children",
        required=False,
        action="store_true",
        help="Pull only the direct children for a code",
    )

    args = parser.parse_args()

    if args.filepath == "rich":
        # For this, if we are writing to a rich table, we will write the log to a file using the default stream handler
        Path("logs").mkdir(parents=True, exist_ok=True)
        logger = getlogger("search", loglevel="DEBUG", filename="logs/search.log")
    else:
        # If we want to write the results to a file, we can configure the rich log handler to make the logging much easier to read.
        logger = getlogger(
            "search",
            loglevel="DEBUG",
            console_handler=RichHandler(rich_tracebacks=True),
        )

    onto_data = ftd_ontology_lookup()
    if args.all_keywords and (args.descendants or args.children):
        args.all_keywords = args.all_keywords.lower().replace("snomedct", "snomed")
    if args.ontologies and (args.descendants or args.children):
        args.ontologies = args.ontologies.lower().replace("snomedct", "snomed")
    if args.descendants and not args.ontologies:
        parser.error("-o/--ontologies is required when -d/--descendants is provided")
    if args.descendants and args.children:
        parser.error(
            "Cannot use -d/--descendants and -c/--children together. Can only use one at a time."
        )
    if args.descendants or args.children:
        args.start_index = 0
        iri_results = []

        if not args.iri or args.parent_data:
            search_results = run_search(
                onto_data,
                args.all_keywords,
                [args.ontologies],
                ["ols2"],
                args.results_per_page,
                args.start_index,
            )
            iri_results = search_results.get("results", [])
        if args.iri:
            iri = args.iri
        else:
            if not iri_results or len(iri_results) == 0:
                print(
                    f"Could not find IRI for {args.all_keywords}. Please try again in a few minutes to ensure this is not an issue with the API."
                )
                return
            iri = iri_results[0].get("code_iri")

        if args.parent_data and iri_results:
            parent_data = iri_results[0]
        else:
            parent_data = None

        desc_search(
            codes=args.all_keywords,
            ontologies=args.ontologies,
            filepath=args.filepath,
            results_per_page=args.results_per_page,
            start_index=args.start_index,
            iri=iri,
            parent_data=parent_data,
            children=args.children,
        )
    else:
        do_search(
            codes=args.all_keywords,
            ontologies=args.ontologies or "HP,HPO,MONDO",
            filepath=args.filepath,
            results_per_page=args.results_per_page,
            start_index=args.start_index,
        )
