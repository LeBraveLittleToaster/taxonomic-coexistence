from collections import defaultdict
from typing import Optional, List, Callable

CONCEPT_FAMILY = "family"
CONCEPT_KINGDOM = "kingdom"
CONCEPT_SUB_FAMILY = "sub_family"
CONCEPT_GENUS = "genus"
CONCEPT_SUB_GENUS = "sub_genus"
CONCEPT_SPECIES = "species"
CONCEPT_SUB_SPECIES = "sub_species"

SCHEMA_IN_SCHEME = "skos:inScheme"  # "skos:concept"
SCHEMA_PREF_LABEL = "skos:prefLabel"
SCHEMA_BROADER = "skos:broader"
SCHEMA_NARROWER = "skos:narrower"
SCHEMA_SYNONYM = "skos:related"
SCHEMA_TAXON_STATUS = "skos:definition"
SCHEMA_HISTORY_NOTE = "skos:historyNote"
SCHEMA_AUTHOR = "skos:scopeNote"


class SkosAttribute:
    """
    SkosAttributes are attributes which should be stored in a node to save values corresponding to this node
    """

    def __init__(self, schema: str, literal: str):
        self.schema = schema
        self.literal = literal

    def __str__(self):
        return "Schema: " + self.schema + " | Literal: " + self.literal


class SkosNode:
    """
    A SkosNode represents a node (like plant, family, genus etc.) with the corresponding attributes.
    A SkosNode is a sub-graph with a central node (descriptor) and the attributes as single leaves
    Leaves are not interconnectabble within a SkosNode
    """

    def __init__(self, descriptor: str, pref_label: str, init_attributes: [SkosAttribute]):
        self.descriptor: str = descriptor
        self.attributes: [SkosAttribute] = []
        self.add_attribute(SCHEMA_PREF_LABEL, pref_label)
        if init_attributes is not None:
            att: SkosAttribute
            for att in init_attributes:
                self.add_attribute(att.schema, att.literal)

    def __str__(self):
        out = "Descriptor: " + str(self.descriptor) + "\n"
        for attribute in self.attributes:
            out += "-> " + str(attribute) + "\n"
        return out

    def add_attribute(self, schema: str, literal: str) -> bool:
        if self.get_attribute_by_schema(schema) is not None:
            return False
        self.attributes.append(SkosAttribute(schema, literal))
        return True

    def get_attribute_by_schema(self, schema: str) -> Optional[SkosAttribute]:
        attribute: SkosAttribute
        for attribute in self.attributes:
            if attribute.schema == schema:
                return attribute
        return None


class SkosRelation:
    """
    SkosRelation´s class represents a unidirectional connection between nodes from start to end
    start is equal to a child in a tree, end to a parent
    visually an arrows would be drawn from start to end
    label is the type of relation
    """

    def __init__(self, start_descriptor: str, label: str, end_descriptor: str):
        self.end_descriptor = end_descriptor
        self.label = label
        self.start_descriptor = start_descriptor

    def __str__(self):
        return "Start: " + str(self.start_descriptor) \
               + " | End: " + str(self.end_descriptor) \
               + " | Label: " + str(self.label)


class SkosGraph:
    """
    A SkosGraph is a container for all nodes and there relations with manipulator methods
    """

    def __init__(self, name=""):
        self.name: str = name
        self.nodes: [SkosNode] = []
        self.relations: [SkosRelation] = []

    def get_outgoing_relations_with_descriptor(self, start_descriptor: str) -> [SkosRelation]:
        return [x for x in self.relations if x.start_descriptor == start_descriptor]

    def get_node_by_descriptor(self, descriptor: str) -> Optional[SkosNode]:
        node: SkosNode
        for node in self.nodes:
            if node.descriptor == descriptor:
                return node
        return None

    def get_node_by_name(self, name: str) -> Optional[SkosNode]:
        node: SkosNode
        for node in self.nodes:
            if node.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal == name:
                return node
        return None

    def get_all_nodes_by_name(self, name: str) -> List[SkosNode]:
        nodes: List[SkosNode] = []
        for node in self.nodes:
            if node.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal == name:
                nodes.append(node)
        return nodes

    def add_kingdom_node(self, descriptor: str,
                         kingdom_name: str = "insert kingdom name here...",
                         attributes: [SkosAttribute] = None) -> SkosNode:
        if attributes is None:
            attributes = []
        node = SkosNode(descriptor, kingdom_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_KINGDOM)
        self.nodes.append(node)
        return node

    def add_family_node(self, descriptor: str,
                        family_name: str = "insert family name here...",
                        attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, family_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_FAMILY)
        self.nodes.append(node)
        return node

    def add_sub_family_node(self, descriptor: str,
                            sub_family_name: str = "insert sub family name here...",
                            attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, sub_family_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_SUB_FAMILY)
        self.nodes.append(node)
        return node

    def add_genus_node(self, descriptor: str,
                       genus_name: str = "insert genus name here...", attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, genus_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_GENUS)
        self.nodes.append(node)
        return node

    def add_sub_genus_node(self, descriptor: str,
                           sub_genus_name: str = "insert sub genus name here...",
                           attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, sub_genus_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_SUB_GENUS)
        self.nodes.append(node)
        return node

    def add_species_node(self, descriptor: str,
                         species_name: str = "insert species name here...",
                         attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, species_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_SPECIES)
        self.nodes.append(node)
        return node

    def add_sub_species_node(self, descriptor: str,
                             sub_species_name: str = "insert species name here...",
                             attributes: [SkosAttribute] = None) -> SkosNode:
        node = SkosNode(descriptor, sub_species_name, attributes)
        node.add_attribute(SCHEMA_IN_SCHEME, CONCEPT_SUB_SPECIES)
        self.nodes.append(node)
        return node

    def add_synonym_relation(self, start_descriptor: str, end_descriptor: str) -> SkosRelation:
        return self.__add_relation(start_descriptor, SCHEMA_SYNONYM, end_descriptor)

    def __add_relation(self, start_descriptor: str, schema: str, end_descriptor: str) -> SkosRelation:
        relation = SkosRelation(start_descriptor, schema, end_descriptor)
        self.relations.append(relation)
        return relation

    def add_family_to_kingdom(self, family_descriptor: str, kingdom_descriptor: str) -> bool:
        return self.__add_node_to_node(family_descriptor, CONCEPT_FAMILY, kingdom_descriptor, CONCEPT_KINGDOM)

    def add_sub_family_to_family(self, sub_family_descriptor: str, family_descriptor: str) -> bool:
        return self.__add_node_to_node(sub_family_descriptor, CONCEPT_SUB_FAMILY, family_descriptor, CONCEPT_FAMILY)

    def add_sub_genus_to_genus(self, sub_genus_descriptor: str, genus_descriptor: str) -> bool:
        return self.__add_node_to_node(sub_genus_descriptor, CONCEPT_SUB_GENUS, genus_descriptor, CONCEPT_GENUS)

    def add_genus_to_family(self, genus_descriptor: str, family_descriptor: str) -> bool:
        return self.__add_node_to_node(genus_descriptor, CONCEPT_GENUS, family_descriptor, CONCEPT_FAMILY)

    def add_genus_to_sub_family(self, genus_descriptor: str, sub_family_descriptor: str) -> bool:
        return self.__add_node_to_node(genus_descriptor, CONCEPT_GENUS, sub_family_descriptor, CONCEPT_SUB_FAMILY)

    def add_species_to_genus(self, species_descriptor: str, genus_descriptor: str) -> bool:
        return self.__add_node_to_node(species_descriptor, CONCEPT_SPECIES, genus_descriptor, CONCEPT_GENUS)

    def add_species_to_sub_genus(self, species_descriptor: str, sub_genus_descriptor: str) -> bool:
        return self.__add_node_to_node(species_descriptor, CONCEPT_SPECIES, sub_genus_descriptor, CONCEPT_SUB_GENUS)

    def add_sub_species_to_species(self, sub_species_descriptor: str, species_descriptor: str) -> bool:
        return self.__add_node_to_node(sub_species_descriptor, CONCEPT_SUB_SPECIES, species_descriptor, CONCEPT_SPECIES)

    # manipulators

    def change_parent(self, parent_descriptor: str, child_descriptor: str, new_parent_descriptor: str):
        relation: SkosRelation
        for relation in self.relations:
            if relation.start_descriptor == child_descriptor and relation.end_descriptor == parent_descriptor:
                relation.end_descriptor = new_parent_descriptor

    # utils methods
    def is_parent_of(self, child_descriptor: str, parent_descriptor: str) -> bool:
        relation: SkosRelation
        for relation in self.relations:
            if relation.start_descriptor == child_descriptor and relation.end_descriptor == parent_descriptor:
                return True
        return False

    # private utils
    def __add_node_to_node(self, descriptor_node_child: str, concept_child: str, descriptor_node_parent: str,
                           concept_parent: str) -> bool:
        self.__add_relation(descriptor_node_child,
                            SCHEMA_BROADER, descriptor_node_parent)
        self.__add_relation(descriptor_node_parent,
                            SCHEMA_NARROWER, descriptor_node_child)
        return True

    # printer and exporter

    def __str__(self):
        out = ""
        for node in self.nodes:
            out += str(node) + "\n"
        for relation in self.relations:
            out += str(relation) + "\n"
        return out

    def to_rdf_skos_str(self) -> str:
        out = ""
        out += "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        out += "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n"
        out += "@prefix example: <http://www.example.com/> .\n\n"
        out += 'example:kingdom rdf:type skos:ConceptScheme; skos:prefLabel "kingdom" .\n'
        out += 'example:family rdf:type skos:ConceptScheme; skos:prefLabel "family" .\n'
        out += 'example:species rdf:type skos:ConceptScheme; skos:prefLabel "species" .\n'
        out += 'example:genus rdf:type skos:ConceptScheme; skos:prefLabel "genus" .\n'

        node: SkosNode
        for node in self.nodes:
            out += "example:" + str(node.descriptor) + " rdf:type skos:Concept;\n"

            lines_out = []
            attribute: SkosAttribute
            for attribute in node.attributes:

                if attribute.schema != SCHEMA_IN_SCHEME:
                    lines_out.append('  ' + attribute.schema + ' "' + attribute.literal + '"')
                else:
                    lines_out.append('  ' + attribute.schema + ' example:' + attribute.literal)
            relation: SkosRelation
            r: SkosRelation
            for relation in [r for r in self.relations if r.start_descriptor == node.descriptor]:
                lines_out.append('  ' + relation.label + ' example:' + relation.end_descriptor + '')

            for i in range(0, len(lines_out)):
                out += lines_out[i]
                if i == len(lines_out) - 1:
                    out += ".\n\n"
                else:
                    out += ";\n"
        return out


def default_pref_label_retriever(node: SkosNode) -> str:
    attribute: SkosAttribute
    for attribute in node.attributes:
        if attribute.schema == SCHEMA_PREF_LABEL:
            return attribute.literal
    raise ValueError("NO ATTRIBUTE PREF_LABEL FOUND")


class NodeSearchIndex:
    def __init__(self, graph: SkosGraph, func: Callable[[SkosNode], str] = default_pref_label_retriever):
        self.key_dict: defaultdict = defaultdict(lambda: [])
        node: SkosNode
        for node in graph.nodes:
            self.key_dict[func(node)].append(node)

    def get_nodes_for_key(self, key) -> Optional[List[SkosNode]]:
        try:
            return self.key_dict[key]
        except KeyError:
            return None

    def get_all_nodes_for_keys(self, keys: List) -> List[SkosNode]:
        l_o_l = [self.key_dict[x] for x in keys]
        return [item for sublist in l_o_l for item in sublist]


def get_next_propagation_descriptors(relations: List[SkosRelation], descriptor: str) -> List[str]:
    result: List[str] = []
    relation: SkosRelation
    for relation in relations:
        if relation.start_descriptor == descriptor:
            result.append(relation.end_descriptor)
        if relation.end_descriptor == descriptor:
            result.append(relation.start_descriptor)
    return result


def get_relations_filtered(relations: List[SkosRelation], schema: str) -> List[SkosRelation]:
    result: List[SkosRelation] = []
    relation: SkosRelation
    for relation in relations:
        if relation.label == schema:
            result.append(relation)
    return result


def remove_duplicates(mlist: List[str]) -> List[str]:
    return list(dict.fromkeys(mlist))


class RelationSearchIndex:
    def __init__(self, graph: SkosGraph):
        self.forward_relation_dict: defaultdict = defaultdict(lambda: [])
        self.backward_relation_dict: defaultdict = defaultdict(lambda: [])
        relation: SkosRelation
        for relation in graph.relations:
            self.forward_relation_dict[relation.start_descriptor].append(relation)
            self.backward_relation_dict[relation.end_descriptor].append(relation)

    def get_all_descriptor_for_descriptor(self, descriptor: str, schema: str) -> List[str]:
        relations: List[SkosRelation] = self.forward_relation_dict[descriptor] + self.backward_relation_dict[descriptor]
        return remove_duplicates(
            get_next_propagation_descriptors(
                get_relations_filtered(relations, schema), descriptor))

    def get_broader_relation(self, descriptor: str) -> Optional[SkosRelation]:
        relations: List[SkosRelation] = self.backward_relation_dict.get(descriptor)
        if relations is None:
            return None
        relation: SkosRelation
        for relation in relations:
            if relation.label == SCHEMA_NARROWER:
                return relation
        return None

    def get_broader_or_synonym_relation(self, descriptor: str, node_search_index: NodeSearchIndex):
        nodes_opt: Optional[List[SkosNode]] = node_search_index.get_nodes_for_key(descriptor)
        if nodes_opt is None or len(nodes_opt) == 0:
            return None
        node: SkosNode = nodes_opt[0]
        if node is None:
            return None

        relations: List[SkosRelation] = self.backward_relation_dict.get(descriptor)
        if relations is None:
            relations = []

        relation: SkosRelation
        for relation in relations:
            if relation.label == SCHEMA_NARROWER:
                return relation

        relations: List[SkosRelation] = self.forward_relation_dict.get(descriptor)
        for relation in relations:
            nodes_end: Optional[List[SkosNode]] = node_search_index.get_nodes_for_key(relation.start_descriptor)
            if len(nodes_end) == 0:
                continue
            node_end: SkosNode = nodes_end[0]
            if relation.label == SCHEMA_SYNONYM \
                    and node.get_attribute_by_schema(SCHEMA_HISTORY_NOTE).literal == node_end.get_attribute_by_schema(
                SCHEMA_HISTORY_NOTE).literal:
                return SkosRelation(relation.end_descriptor, relation.label, relation.start_descriptor)
        return None
