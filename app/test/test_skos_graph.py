import random
from unittest import TestCase

from graph.skos_graph import SkosGraph, NodeSearchIndex, RelationSearchIndex, SkosNode
from graph.skos_graph_utils import get_node_hierarchy_upwards_from, save_graph_to_file, load_graph_from_file, \
    load_test_graph, get_hierarchy_upwards_from


class TestSkosGraph(TestCase):

    def test_load_test_graph(self):
        graph = load_test_graph()
        print(graph.to_rdf_skos_str())

    def test_first_graph(self):
        graph = load_graph_from_file("../tpl")
        print("wtf")

    def test_change_parent(self):
        self.graph: SkosGraph = SkosGraph()

        # kingdom
        self.graph.add_kingdom_node("k1", "KingdomName1")

        # family
        self.graph.add_family_node("f1", "FamilyName1")
        self.graph.add_family_to_kingdom("f1", "k1")

        # Genus
        self.graph.add_genus_node("g1", "g1_n")
        self.graph.add_genus_node("g2", "g2_n")
        self.graph.add_genus_to_family("g1", "f1")
        self.graph.add_genus_to_family("g2", "f1")

        # Plants
        self.graph.add_species_node("s1", "s1_n")
        self.graph.add_species_node("s2", "s2_n")
        self.graph.add_species_to_genus("s1", "g1")
        self.graph.add_species_to_genus("s2", "g1")

        # relations
        self.graph.add_synonym_relation("s1", "s2")

        if not self.graph.is_parent_of("s2", "g1"):
            self.fail("s2 not parent of g1")

        self.graph.change_parent("g1", "s2", "g2")

        if not self.graph.is_parent_of("s2", "g2"):
            self.fail("s2 not parent of g2")

        print("*++++++++++++++++++++++++*\n")
        print(self.graph.to_skos_str())
        print("*++++++++++++++++++++++++*\n")
        print("Upwards hierarchy of s2")
        for e in list(map(lambda x: str(x.descriptor), get_node_hierarchy_upwards_from(self.graph, "s2"))):
            print(" -> " + e, end="")

        print("*++++++++++++++++++++++++*\n")
        print(self.graph.to_rdf_skos_str())
        print("*++++++++++++++++++++++++*\n")

        save_graph_to_file(self.graph, "out.graph")
        # print(load_graph_to_file("out.graph").to_rdf_skos_str())

    def test_hierarchy_graph(self):

        self.graph = load_graph_from_file("../application/generated.graph")

        t_node:SkosNode = self.graph.nodes[random.randint(0, len(self.graph.nodes))]

        print("Building relation indexes...")
        relation_search_index: RelationSearchIndex = RelationSearchIndex(self.graph)
        print("Building descriptor node indexes...")
        descriptor_node_search_index: NodeSearchIndex = NodeSearchIndex(self.graph, lambda x: x.descriptor)
        l = get_hierarchy_upwards_from(t_node.descriptor, relation_search_index, descriptor_node_search_index)
        print(l)
