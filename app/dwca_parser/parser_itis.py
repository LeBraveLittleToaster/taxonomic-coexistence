import logging

from pandas import DataFrame

from dwca_parser.dwca_fields import *
from dwca_parser.parser_base import ParserBase
from graph.skos_graph import SkosGraph, SkosAttribute, SCHEMA_TAXON_STATUS, SCHEMA_AUTHOR


class ParserITIS(ParserBase):
    log: logging

    def __init__(self, dataframe: DataFrame, name: str, target_kingdoms=None):
        super().__init__(dataframe, name, target_kingdoms)
        self.log = logging.getLogger("Parser-ITIS")

    def _parse(self) -> SkosGraph:
        self.log.info("Start parsing")
        kingdoms: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_TAXON_RANK].map(str.upper).isin([FIELD_KINGDOM.upper()])
        ]
        for index, row in kingdoms.iterrows():
            if row[FIELD_SCIENTIFIC_NAME].upper() in self.target_kingdoms:
                self.graph.add_kingdom_node(str(row[FIELD_ID]), row[FIELD_SCIENTIFIC_NAME],
                                            [SkosAttribute(SCHEMA_TAXON_STATUS, row[FIELD_TAXONOMIC_STATUS]),
                                             SkosAttribute(SCHEMA_AUTHOR, "")])
                self.__find_sub_nodes(row[FIELD_ID], row[FIELD_ID], FIELD_FAMILY, FIELD_FAMILY)
        self.log.info("Parsing finished")
        return self.graph

    def __find_sub_nodes(self,
                         parent_id,
                         top_parent_id,
                         curr_search_level,
                         parent_search_level):
        self.log.info("Parse level: " + curr_search_level)
        childs: DataFrame = self.dataframe[self.dataframe[FIELD_PARENT_NAME_USAGE_ID] == parent_id]
        for index, row in childs.iterrows():
            if row[FIELD_TAXON_RANK].lower() == curr_search_level:
                self.__add_node_to_skos_graph(row, top_parent_id, curr_search_level, parent_search_level)
                self.__find_synonyms(row[FIELD_ID], curr_search_level)
                for search_level in self._get_next_search_levels(curr_search_level):
                    self.__find_sub_nodes(row[FIELD_ID], row[FIELD_ID], search_level,
                                          curr_search_level)
            else:
                self.__find_sub_nodes(row[FIELD_ID], top_parent_id, curr_search_level,
                                      parent_search_level)

    def __add_node_to_skos_graph(self,
                                 curr_row,
                                 top_parent_id,
                                 curr_search_level,
                                 parent_search_level):
        author = super()._get_author_str(curr_row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
        if curr_search_level == FIELD_FAMILY:
            self._add_family_to_graph(curr_row, top_parent_id, curr_row[FIELD_TAXONOMIC_STATUS], author)
        elif curr_search_level == FIELD_SUB_FAMILY:
            self._add_sub_family_to_graph(curr_row, top_parent_id, curr_row[FIELD_TAXONOMIC_STATUS], author)
        elif curr_search_level == FIELD_GENUS:
            self._add_genus_to_graph(curr_row, top_parent_id, parent_search_level, curr_row[FIELD_TAXONOMIC_STATUS], author)
        elif curr_search_level == FIELD_SUB_GENUS:
            self._add_sub_genus_to_graph(curr_row, top_parent_id, curr_row[FIELD_TAXONOMIC_STATUS], author)
        elif curr_search_level == FIELD_SPECIES:
            self._add_species_to_graph(curr_row, top_parent_id, parent_search_level, curr_row[FIELD_TAXONOMIC_STATUS], author)
        elif curr_search_level == FIELD_SUB_SPECIES:
            self._add_sub_species_to_graph(curr_row, top_parent_id, curr_row[FIELD_TAXONOMIC_STATUS], author)

    def __find_synonyms(self, accepted_name_usage_id, curr_search_level):
        synonyms: DataFrame = self.dataframe[self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID] == str(accepted_name_usage_id)]
        for index, row in synonyms.iterrows():
            self.__add_synonym_to_graph(row, accepted_name_usage_id, curr_search_level)

    def __add_synonym_to_graph(self, curr_row, parent_id, curr_search_level):
        author = super()._get_author_str(curr_row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
        if curr_search_level == FIELD_FAMILY:
            self.graph.add_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                       [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                        SkosAttribute(SCHEMA_AUTHOR, author)])
        elif curr_search_level == FIELD_SUB_FAMILY:
            self.graph.add_sub_family_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                           [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                            SkosAttribute(SCHEMA_AUTHOR, author)])
        elif curr_search_level == FIELD_GENUS:
            self.graph.add_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                      [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                       SkosAttribute(SCHEMA_AUTHOR, author)])
        elif curr_search_level == FIELD_SUB_GENUS:
            self.graph.add_sub_genus_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                          [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                           SkosAttribute(SCHEMA_AUTHOR, author)])
        elif curr_search_level == FIELD_SPECIES:
            self.graph.add_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                        [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                         SkosAttribute(SCHEMA_AUTHOR, author)])
        elif curr_search_level == FIELD_SUB_SPECIES:
            self.graph.add_sub_species_node(str(curr_row[FIELD_ID]), curr_row[FIELD_SCIENTIFIC_NAME],
                                            [SkosAttribute(SCHEMA_TAXON_STATUS, curr_row[FIELD_TAXONOMIC_STATUS]),
                                             SkosAttribute(SCHEMA_AUTHOR, author)])
        self.graph.add_synonym_relation(str(curr_row[FIELD_ID]), str(parent_id))


