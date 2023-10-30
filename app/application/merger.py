from graph.skos_graph import SkosGraph
from graph.skos_graph_utils import save_graph_to_file, load_graph_from_file, merge_graphs

if __name__ == '__main__':
    print("Loading itis data...")
    graph_itis: SkosGraph = load_graph_from_file("itis.graph")
    print("Loading tpl data...")
    graph_tpl: SkosGraph = load_graph_from_file("tpl.graph")
    print("Loading wfo data...")
    graph_wfo: SkosGraph = load_graph_from_file("wfo.graph")
    print("Loading merging data...")
    graph: SkosGraph = merge_graphs(graph_itis, graph_tpl, graph_wfo)
    print("Saving graph")
    save_graph_to_file(graph, "generated.graph")

    l_itis_nodes = len(graph_itis.nodes)
    l_itis_relations = len(graph_itis.relations)
    l_tpl_nodes = len(graph_tpl.nodes)
    l_tpl_relations = len(graph_tpl.relations)
    l_wfo_nodes = len(graph_wfo.nodes)
    l_wfo_relations = len(graph_wfo.relations)
    l_generated_nodes = len(graph.nodes)
    l_generated_relations = len(graph.relations)

    print("Stats:")
    print("  -> ITIS")
    print("     Node Count: " + str(l_itis_nodes))
    print("     Relation Count: " + str(l_itis_relations))
    print("  -> TPL")
    print("     Node Count: " + str(l_tpl_nodes))
    print("     Relation Count: " + str(l_tpl_relations))
    print("  -> WFO")
    print("     Node Count: " + str(l_wfo_nodes))
    print("     Relation Count: " + str(l_wfo_relations))
    print("  -> GENERATED")
    print("     Node Count: " + str(l_generated_nodes))
    print("     Relation Count: " + str(l_generated_relations))
    print("  -> Newly added nodes: " + str(
        l_generated_relations - l_tpl_relations - l_wfo_relations - l_itis_relations))
    print("  -> Node count difference (should be zero): " + str(
        l_generated_nodes - l_tpl_nodes - l_wfo_nodes - l_itis_nodes))
