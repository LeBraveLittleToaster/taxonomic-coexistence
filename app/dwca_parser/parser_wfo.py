import logging
from typing import Optional, Tuple

from pandas import DataFrame, Series

from dwca_parser.dwca_fields import *
from dwca_parser.parser_base import ParserBase
from graph.skos_graph import SkosGraph, SkosAttribute, SCHEMA_TAXON_STATUS, SCHEMA_AUTHOR


class ParserWFO(ParserBase):
    log: logging
    GENERATED_ID_PREFIX = "wfo-g-"

    def __init__(self, dataframe: DataFrame, name: str, target_kindoms=None):
        super().__init__(dataframe, name, target_kindoms)
        self.log = logging.getLogger("Parser-WFO")

    def _parse(self) -> SkosGraph:
        self.log.info("Start parsing")
        desc_dict_numbers = {}
        desc_dict_id = {}
        self.__load_kingdoms_from_column(desc_dict_numbers)
        self.__load_families_from_column(desc_dict_numbers, desc_dict_id)
        self.__load_genus_from_column(desc_dict_numbers, desc_dict_id)
        self.__load_species_with_synonyms(desc_dict_numbers, desc_dict_id)
        self.__load_sub_species()
        self.log.info("Parsing finished")
        return self.graph

    def __load_kingdoms_from_column(self, desc_dict: dict):
        self.log.info("Parse Kingdoms")
        all_kingdoms: list = self.dataframe[FIELD_KINGDOM].unique().tolist()
        for kingdom in all_kingdoms:
            if kingdom.upper() in self.target_kingdoms:
                desc = 0 if not desc_dict else max(desc_dict.values()) + 1
                gen_desc = super()._get_generated_id(desc)
                self.graph.add_kingdom_node(gen_desc, kingdom, [SkosAttribute(SCHEMA_TAXON_STATUS, "Accepted"),
                                                                SkosAttribute(SCHEMA_AUTHOR, "")])
                desc_dict[kingdom] = desc

    def __load_families_from_column(self, desc_dict_number: dict, desc_dict_id: dict):
        self.log.info("Parse Families")
        relevant_df: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_KINGDOM].map(str.upper).isin(self.target_kingdoms)
        ]
        relevant_df = relevant_df.drop_duplicates(subset=FIELD_FAMILY)
        family_rows: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_FAMILY.upper()
        ]
        for index, row in relevant_df.iterrows():
            desc, has_id = self.__get_id_of(row[FIELD_FAMILY], family_rows)
            gen_desc = ""
            if not has_id:
                desc = 0 if not desc_dict_number else max(desc_dict_number.values()) + 1
                gen_desc = super()._get_generated_id(desc)
            else:
                gen_desc = desc[FIELD_ID]
            parent_desc = desc_dict_number[row[FIELD_KINGDOM]]
            gen_parent_desc = super()._get_generated_id(parent_desc)
            if not has_id:
                self.graph.add_family_node(gen_desc, str(row[FIELD_FAMILY]),
                                           [SkosAttribute(SCHEMA_TAXON_STATUS, "Unknown"),
                                            SkosAttribute(SCHEMA_AUTHOR, "")])
            else:
                author = super()._get_author_str(desc[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
                self.graph.add_family_node(gen_desc, str(row[FIELD_FAMILY]),
                                           [SkosAttribute(SCHEMA_TAXON_STATUS, desc[FIELD_TAXONOMIC_STATUS]),
                                            SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_family_to_kingdom(gen_desc, gen_parent_desc)
            if has_id:
                desc_dict_id[row[FIELD_FAMILY]] = desc[FIELD_ID]
            else:
                desc_dict_number[row[FIELD_FAMILY]] = desc

    def __load_genus_from_column(self, desc_dict_number: dict, desc_dict_id: dict):
        self.log.info("Parse Genus")
        relevant_df: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_KINGDOM].map(str.upper).isin(self.target_kingdoms)
        ]
        relevant_df = relevant_df.drop_duplicates(subset=FIELD_GENUS)
        genus_rows: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_GENUS.upper()
        ]
        for index, row in relevant_df.iterrows():
            desc, has_id = self.__get_id_of(row[FIELD_GENUS], genus_rows)
            gen_desc = ""
            if not has_id:
                desc = 0 if not desc_dict_number else max(desc_dict_number.values()) + 1
                gen_desc = super()._get_generated_id(desc)
            else:
                gen_desc = desc[FIELD_ID]
            parent_desc = ""
            gen_parent_desc = ""
            if row[FIELD_FAMILY] in desc_dict_number:
                parent_desc = desc_dict_number[row[FIELD_FAMILY]]
                gen_parent_desc = super()._get_generated_id(parent_desc)
            if row[FIELD_FAMILY] in desc_dict_id:
                parent_desc = desc_dict_id[row[FIELD_FAMILY]]
                gen_parent_desc = parent_desc
            if not has_id:
                self.graph.add_genus_node(gen_desc, str(row[FIELD_GENUS]),
                                          [SkosAttribute(SCHEMA_TAXON_STATUS, "Unknown"),
                                           SkosAttribute(SCHEMA_AUTHOR, "")])
            else:
                author = super()._get_author_str(desc[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
                self.graph.add_genus_node(gen_desc, str(row[FIELD_GENUS]),
                                          [SkosAttribute(SCHEMA_TAXON_STATUS, desc[FIELD_TAXONOMIC_STATUS]),
                                           SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_genus_to_family(gen_desc, gen_parent_desc)
            if has_id:
                desc_dict_id[row[FIELD_GENUS]] = desc[FIELD_ID]
            else:
                desc_dict_number[row[FIELD_GENUS]] = desc

    def __load_species_with_synonyms(self, desc_dict_number: dict, desc_dict_id: dict):
        self.log.info("Parse Species")
        species_df: DataFrame = self.dataframe[
            (self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_SPECIES.upper())
            & self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID].isna()
        ]
        for index, row in species_df.iterrows():
            parent_desc = ""
            gen_parent_desc = ""
            if row[FIELD_GENUS] in desc_dict_number:
                parent_desc = desc_dict_number[row[FIELD_GENUS]]
                gen_parent_desc = super()._get_generated_id(parent_desc)
            if row[FIELD_GENUS] in desc_dict_id:
                gen_parent_desc = desc_dict_id[row[FIELD_GENUS]]
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            super()._add_species_to_graph(row, gen_parent_desc, FIELD_GENUS, row[FIELD_TAXONOMIC_STATUS], author)
        species_synonym_df: DataFrame = self.dataframe[
            (self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_SPECIES.upper()) &
            (self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID] == self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID])
        ]
        for index, row in species_synonym_df.iterrows():
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            self.graph.add_species_node(str(row[FIELD_ID]), row[FIELD_SCIENTIFIC_NAME],
                                        [SkosAttribute(SCHEMA_TAXON_STATUS, row[FIELD_TAXONOMIC_STATUS]),
                                         SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_synonym_relation(str(row[FIELD_ID]), str(row[FIELD_ACCEPTED_NAME_USAGE_ID]))

    def __load_sub_species(self):
        self.log.info("Parse Sub-Species")
        sub_species_df: DataFrame = self.dataframe[
            self.__get_non_species_cond() &
            self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID].isna()
            ]
        for index, row in sub_species_df.iterrows():
            parent_name = row[FIELD_GENUS] + " " + row[FIELD_SPECIFIC_EPHITHET]
            parent_nodes = self.graph.get_all_nodes_by_name(parent_name)
            parent_desc = ""
            parent_row = self.dataframe[
                (self.dataframe[FIELD_SCIENTIFIC_NAME] == parent_name) &
                (self.dataframe[FIELD_TAXONOMIC_STATUS].map(str).map(str.upper) == STATUS_ACCEPTED.upper())
            ]
            if parent_row.empty:
                self.log.warn("Parent not found: " + parent_name)
            else:
                parent_desc = parent_row.iloc[0][FIELD_ID]
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            super()._add_sub_species_to_graph(row, str(parent_desc), row[FIELD_TAXONOMIC_STATUS], author)

        sub_species_synonyms_df: DataFrame = self.dataframe[
            self.__get_non_species_cond() &
            (self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID] == self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID])
            ]
        for index, row in sub_species_synonyms_df.iterrows():
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            self.graph.add_sub_species_node(row[FIELD_ID], row[FIELD_SCIENTIFIC_NAME],
                                            [SkosAttribute(SCHEMA_TAXON_STATUS, row[FIELD_TAXONOMIC_STATUS]),
                                             SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_synonym_relation(row[FIELD_ID], row[FIELD_ACCEPTED_NAME_USAGE_ID])

    def __get_non_species_cond(self):
        return (self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_SUB_SPECIES.upper()) | \
               (self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_FORM_WFO.upper()) | \
               (self.dataframe[FIELD_TAXON_RANK].map(str.upper) == FIELD_VARIETY_TPL.upper())

    @staticmethod
    def __get_id_of(scientific_name: str, search_df: DataFrame) -> Tuple[Optional[Series], bool]:
        reduced_df: DataFrame = search_df.loc[search_df[FIELD_SCIENTIFIC_NAME] == scientific_name]
        return (None, False) if reduced_df.empty else (reduced_df.iloc[0], True)

