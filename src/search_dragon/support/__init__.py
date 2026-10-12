import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from csv import DictReader, Error
from dataclasses import dataclass, fields
from enum import StrEnum
from typing import IO, Any, Optional

if sys.version_info >= (3, 9):
    from importlib import resources as importlib_resources
else:
    import importlib_resources

import logging

logger = logging.getLogger(__name__)

_support_details = importlib_resources.files("search_dragon") / "support"


class SourceType(StrEnum):
    OWL = "OWL"
    OMOP = "OMOP"
    FHIR = "FHIR"


@dataclass
class Vocabulary:
    name: str
    description: str | None
    prefix: str
    fhir_system: str
    uri: str
    source_type: SourceType | None
    source_filename: str | None
    synonym: str  # list[str]
    api_preference: str  # Optional[dict[str, str]]

    @classmethod
    def fieldnames(cls):
        return [field.name for field in fields(cls)]

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Vocabulary":
        """Build a Vocabulary from a CSV row, converting empty strings to None
        and the source_type string to a SourceType."""
        source_type = row.get("source_type") or None
        return cls(
            name=row["name"],
            description=row.get("description") or None,
            prefix=row["prefix"],
            fhir_system=row["fhir_system"],
            uri=row["uri"],
            source_type=SourceType(source_type) if source_type else None,
            source_filename=row.get("source_filename") or None,
            synonym=row["synonym"],
            api_preference=row["api_preference"],
        )


@contextmanager
def open_resource(
    resource_filename, mode: str = "rt", **open_kwargs: Any
) -> Iterator[IO[Any]]:
    """Open a package resource or path and yield the open file.

    Use as a context manager. The file (and any temporary extraction
    done by importlib_resources.as_file) is cleaned up on exit.
    Extra keyword arguments (encoding, newline, etc.) go to open().
    """
    resource = _support_details / resource_filename
    with (
        importlib_resources.as_file(resource) as path,
        open(path, mode, **open_kwargs) as infile,
    ):
        yield infile


def load_vocabulary_details(csv_path=None):
    if csv_path == None:
        csv_path = "vocabulary_details.csv"

    vocabularies = []
    try:
        with open_resource(csv_path, encoding="utf-8") as infile:
            vocabularies = [
                Vocabulary.from_row(row)
                for row in DictReader(infile, delimiter=",", quotechar='"')
            ]
    except (OSError, UnicodeDecodeError, Error, KeyError) as e:
        logger.error(
            f"An error was encountered when loading FTD Ontological Lookup data: {e}"
        )

    return vocabularies


def ftd_ontology_lookup(csv_path=None):
    """Return the lookup as a dictionary: curie=>system"""
    onto_data = {}

    visited_prefixes = set()
    if csv_path is None:
        csv_path = "ftd_ontology_lookup.csv"

        # Let's preference our vocabulary list
        vocabularies = load_vocabulary_details()

        for voc in vocabularies:
            onto_data[voc.prefix] = voc.fhir_system
            visited_prefixes |= set([voc.prefix] + voc.synonym.split(","))

    try:
        with open_resource(csv_path, encoding="utf-8") as infile:
            lkup = DictReader(infile, delimiter=",", quotechar='"')
            for row in lkup:
                if row["curie"] not in visited_prefixes:
                    onto_data[row["curie"]] = row["system"]
    except (OSError, UnicodeDecodeError, Error, KeyError) as e:
        logger.error(
            f"An error was encountered when loading FTD Ontological Lookup data: {e}"
        )

    return onto_data
