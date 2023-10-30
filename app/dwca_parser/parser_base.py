from abc import abstractmethod
from typing import List

from pandas import DataFrame

from dwca_parser.dwca_fields import *
from graph.skos_graph import SkosGraph, SkosAttribute, SCHEMA_TAXON_STATUS, SCHEMA_AUTHOR

_DEFAULT_KINGDOM = "PLANTAE"


class ParserBase(object):
    dataframe: DataFrame
    target_kingdoms: List[str]
    graph: SkosGraph
    GENERATED_ID_PREFIX: str

    def __init__(self, dataframe: DataFrame, name: str, target_kingdoms=None) -> None:
        self.dataframe = dataframe
        self.graph = SkosGraph(name)
        if target_kingdoms is None:
            self.target_kingdoms = [_DEFAULT_KINGDOM]

    def process(self) -> SkosGraph:
        return self._parse()

    @abstractmethod
    def _parse(self) -> SkosGraph:
        raise NotImplementedError

    def _add_family_to_graph(self, curr_row, kingdom_id, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                       [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                        SkosAttribute(SCHEMA_AUTHOR, author)])
        self.graph.add_family_to_kingdom(str(curr_row[FIELD_ID]), str(kingdom_id))

    def _add_sub_family_to_graph(self, curr_row, parent_id, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_sub_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_sub_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                           [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                            SkosAttribute(SCHEMA_AUTHOR, author)])
        self.graph.add_family_to_kingdom(str(curr_row[FIELD_ID]), str(parent_id))

    def _add_genus_to_graph(self, curr_row, parent_id, parent_search_level, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                      [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                       SkosAttribute(SCHEMA_AUTHOR, author)])
        if parent_search_level == FIELD_FAMILY:
            self.graph.add_genus_to_family(str(curr_row[FIELD_ID]), str(parent_id))
        else:
            self.graph.add_genus_to_sub_family(str(curr_row[FIELD_ID]), str(parent_id))

    def _add_sub_genus_to_graph(self, curr_row, parent_id, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_sub_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_sub_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                          [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                           SkosAttribute(SCHEMA_AUTHOR, author)])
        self.graph.add_sub_genus_to_genus(str(curr_row[FIELD_ID]), str(parent_id))

    def _add_species_to_graph(self, curr_row, parent_id, parent_search_level=FIELD_GENUS, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                        [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                         SkosAttribute(SCHEMA_AUTHOR, author)])
        if parent_search_level == FIELD_GENUS:
            self.graph.add_species_to_genus(str(curr_row[FIELD_ID]), str(parent_id))
        else:
            self.graph.add_genus_to_sub_family(str(curr_row[FIELD_ID]), str(parent_id))

    def _add_sub_species_to_graph(self, curr_row, parent_id, taxon_status="", author=""):
        if taxon_status == "":
            self.graph.add_sub_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME])
        else:
            self.graph.add_sub_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                            [SkosAttribute(SCHEMA_TAXON_STATUS, taxon_status),
                                             SkosAttribute(SCHEMA_AUTHOR, author)])
        self.graph.add_sub_species_to_species(str(curr_row[FIELD_ID]), str(parent_id))

    @staticmethod
    def _get_next_search_levels(curr_search_level: str) -> List[str]:
        if curr_search_level == FIELD_FAMILY:
            return [FIELD_SUB_FAMILY, FIELD_GENUS]
        elif curr_search_level == FIELD_SUB_FAMILY:
            return [FIELD_GENUS]
        elif curr_search_level == FIELD_GENUS:
            return [FIELD_SUB_GENUS, FIELD_SPECIES]
        elif curr_search_level == FIELD_SUB_GENUS:
            return [FIELD_SPECIES]
        elif curr_search_level == FIELD_SPECIES:
            return [FIELD_SUB_SPECIES]
        else:
            return []

    def _get_generated_id(self, desc: int) -> str:
        return self.GENERATED_ID_PREFIX + str(desc)

    def _get_author_str(self, author_field: str) -> str:
        author = ""
        if not str(author_field) == "nan":
            author = author_field
        return author
