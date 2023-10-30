import logging

from pandas import DataFrame

from dwca_parser.dwca_fields import *
from dwca_parser.parser_base import ParserBase
from graph.skos_graph import SkosGraph, SkosAttribute, SCHEMA_TAXON_STATUS, SCHEMA_AUTHOR


class ParserTPL(ParserBase):
    log: logging
    GENERATED_ID_PREFIX = "tpl-g-"

    def __init__(self, dataframe: DataFrame, name: str, target_kingdoms=None):
        super().__init__(dataframe, name, target_kingdoms)
        self.log = logging.getLogger("Parser-TPL")

    def _parse(self) -> SkosGraph:
        self.log.info("Start parsing")
        desc_dict = {}
        self.__load_kingdoms_from_column(desc_dict)
        self.__load_families_from_column(desc_dict)
        self.__load_genus_from_column(desc_dict)
        self.__add_species_with_synonyms(desc_dict)
        self.__add_sub_species()
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

    def __load_families_from_column(self, desc_dict: dict):
        self.log.info("Parse Families")
        relevant_df: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_KINGDOM].map(str.upper).isin(self.target_kingdoms)
        ]
        relevant_df = relevant_df.drop_duplicates(subset=FIELD_FAMILY)
        for index, row in relevant_df.iterrows():
            desc = 0 if not desc_dict else max(desc_dict.values()) + 1
            parent_desc = desc_dict[row[FIELD_KINGDOM]]
            gen_desc = super()._get_generated_id(desc)
            gen_parent_desc = super()._get_generated_id(parent_desc)
            self.graph.add_family_node(gen_desc, str(row[FIELD_FAMILY]), [SkosAttribute(SCHEMA_TAXON_STATUS, "Unknown"),
                                                                          SkosAttribute(SCHEMA_AUTHOR, "")])
            self.graph.add_family_to_kingdom(gen_desc, gen_parent_desc)
            desc_dict[row[FIELD_FAMILY]] = desc

    def __load_genus_from_column(self, desc_dict: dict):
        self.log.info("Parse Genus")
        relevant_df: DataFrame = self.dataframe.loc[
            self.dataframe[FIELD_KINGDOM].map(str.upper).isin(self.target_kingdoms)
        ]
        relevant_df = relevant_df.drop_duplicates(subset=FIELD_GENUS)
        for index, row in relevant_df.iterrows():
            desc = 0 if not desc_dict else max(desc_dict.values()) + 1
            parent_desc = desc_dict[row[FIELD_FAMILY]]
            gen_desc = super()._get_generated_id(desc)
            gen_parent_desc = super()._get_generated_id(parent_desc)
            self.graph.add_genus_node(gen_desc, row[FIELD_GENUS], [SkosAttribute(SCHEMA_TAXON_STATUS, "Unknown"),
                                                                   SkosAttribute(SCHEMA_AUTHOR, "")])
            self.graph.add_family_to_kingdom(gen_desc, gen_parent_desc)
            desc_dict[row[FIELD_GENUS]] = desc

    def __add_species_with_synonyms(self, desc_dict: dict):
        self.log.info("Parse Species")
        species_df: DataFrame = self.dataframe[
            (self.dataframe[FIELD_TAXON_RANK] == FIELD_SPECIES) & self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID].isna()
            ]
        for index, row in species_df.iterrows():
            parent_desc = desc_dict[row[FIELD_GENUS]]
            gen_parent_desc = super()._get_generated_id(parent_desc)
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            super()._add_species_to_graph(row, gen_parent_desc, FIELD_GENUS, row[FIELD_TAXONOMIC_STATUS], author)

        species_synonym_df: DataFrame = self.dataframe[(self.dataframe[FIELD_TAXON_RANK] == FIELD_SPECIES) &
                                                       (self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID] == self.dataframe[
                                                           FIELD_ACCEPTED_NAME_USAGE_ID])]
        for index, row in species_synonym_df.iterrows():
            author = super()._get_author_str(row[FIELD_SCIENTIFIC_NAME_AUTHORSHIP])
            self.graph.add_species_node(str(row[FIELD_ID]), row[FIELD_SCIENTIFIC_NAME],
                                        [SkosAttribute(SCHEMA_TAXON_STATUS, row[FIELD_TAXONOMIC_STATUS]),
                                         SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_synonym_relation(str(row[FIELD_ID]), str(row[FIELD_ACCEPTED_NAME_USAGE_ID]))

    def __add_sub_species(self):
        self.log.info("Parse Sub-Species")
        sub_species_df: DataFrame = self.dataframe[
            self.__get_non_species_cond() &
            self.dataframe[FIELD_ACCEPTED_NAME_USAGE_ID].isna()
        ]
        for index, row in sub_species_df.iterrows():
            parent_name = row[FIELD_GENUS] + " " + row[FIELD_SPECIFIC_EPHITHET]
            parent_desc = ""
            parent_row = self.dataframe[
                (self.dataframe[FIELD_SCIENTIFIC_NAME] == parent_name) &
                (self.dataframe[FIELD_TAXONOMIC_STATUS] == STATUS_ACCEPTED)
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
            self.graph.add_sub_species_node(str(row[FIELD_ID]), row[FIELD_SCIENTIFIC_NAME],
                                            [SkosAttribute(SCHEMA_TAXON_STATUS, row[FIELD_TAXONOMIC_STATUS]),
                                             SkosAttribute(SCHEMA_AUTHOR, author)])
            self.graph.add_synonym_relation(str(row[FIELD_ID]), str(row[FIELD_ACCEPTED_NAME_USAGE_ID]))

    def __get_non_species_cond(self):
        return (self.dataframe[FIELD_TAXON_RANK] == FIELD_SUB_SPECIES) | \
               (self.dataframe[FIELD_TAXON_RANK] == FIELD_FORM_TPL) | \
               (self.dataframe[FIELD_TAXON_RANK] == FIELD_VAR_TPL) | \
               (self.dataframe[FIELD_TAXON_RANK] == FIELD_VAR_SCHN_TPL) | \
               (self.dataframe[FIELD_TAXON_RANK] == FIELD_VARIETY_TPL)
