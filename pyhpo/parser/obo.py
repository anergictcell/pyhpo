"""
Parse the OBO flat-file
"""
import os
from typing import Callable, Dict, Iterator, List

from pyhpo.config import TRUTH


FILENAME = 'hp.obo'


class Metadata:
    format_version: str
    data_version: str
    header: List[str] = []

    @classmethod
    def add_header_row(cls, row: str) -> None:
        cls.header.append(row)


class Converter:
    key_conversion: Dict[str, str] = {
        'def': 'definition'
    }

    type_conversions: Dict[str, Callable] = {}

    @classmethod
    def add_type_conversion(cls, key: str, func: Callable) -> None:
        cls.type_conversions[key] = func

    @staticmethod
    def array_to_str(
        value: List[str],
        key: str,
        values: List[List[str]]
    ) -> str:
        if len(value):
            return value[0]
        return ''

    @staticmethod
    def array_to_bool(
        value: List[str],
        key: str,
        values: List[List[str]]
    ) -> bool:
        if not len(value):
            return False
        return value[0].lower() in TRUTH

    @staticmethod
    def parse_synonym(
        value: List[str],
        key: str,
        values: List[List[str]]
    ) -> List[str]:
        """
        Extracts the synonym from the synonym data line in the obo file format

        Parameters
        ----------
        synonym: str
            value part of synonym-data line of obo file

            e.g: "Multicystic dysplastic kidney" EXACT []

        Returns
        -------
        str
            Actual synonym title

            e.g.: Multicystic dysplastic kidney
        """
        return [x.split('"')[1] for x in value]


Converter.add_type_conversion('id', Converter.array_to_str)
Converter.add_type_conversion('name', Converter.array_to_str)
Converter.add_type_conversion('comment', Converter.array_to_str)
Converter.add_type_conversion('definition', Converter.array_to_str)
Converter.add_type_conversion('is_obsolete', Converter.array_to_bool)
Converter.add_type_conversion('replaced_by', Converter.array_to_str)
Converter.add_type_conversion('synonym', Converter.parse_synonym)


def terms_from_file(data_folder: str) -> Iterator[dict]:
    """
    Reads an obo file line by line to yield
    a dict for building an HPOTerm

    Parameters
    ----------
    data_folder:
        Full path to ``obo`` file

    """
    filename = os.path.join(data_folder, FILENAME)

    with open(filename) as fh:
        # everything above the first [Term] is header
        # and thus must not be parsed as term
        for line in fh:
            line = line.strip()
            if line == '[Term]':
                break
            else:
                Metadata.add_header_row(line)

        term_section: List[str] = []
        for line in fh:
            line = line.strip()
            if line == '[Term]':
                yield parse_obo_section(term_section)
                term_section = []
            elif line == "[Typedef]":
                # we're currently not parsing an Typedef section.
                # Since they only appear at the end of the OBO file
                # we're stopping the parsing here.
                # TODO: Instead of break, add logic to skip all Typedef
                # sections and continue with term parsing
                break
            else:
                term_section.append(line)

        yield parse_obo_section(term_section)


def parse_obo_section(term_section: List[str]) -> dict:
    """
    Parses the section of an OBO file for one single HPO term

    Parameters
    ----------
    term_section:
        Lines of the ``obo`` file that describe the HPO term
    """
    term_data = {}
    for line in term_section:
        if line == '':
            continue
        key, value = line.split(':', 1)
        if key not in term_data:
            term_data[key] = [value.strip()]
        else:
            term_data[key].append(value.strip())
    term_dict = _convert_dict_keys(term_data)
    term_dict = _convert_value_types(term_data)
    return term_dict


def _convert_dict_keys(term_data: dict) -> dict:
    """
    The HPO obo flat file contains some unfortunate attribute names.
    This function will convert them into the actual attributes
    for ``HPOTerm``
    """

    for old, new in Converter.key_conversion.items():
        term_data[new] = term_data.pop(old, [])

    return term_data


def _convert_value_types(term_data: dict) -> dict:
    for key, convert in Converter.type_conversions.items():
        term_data[key] = convert(
            term_data.get(key, []),
            key,
            term_data
        )

    return term_data
