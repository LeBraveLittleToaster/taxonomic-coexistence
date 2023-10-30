from graph.MultiThreadExport import to_skos_export
from graph.skos_graph import SkosGraph, RelationSearchIndex
from graph.skos_graph_utils import load_graph_from_file

print("Loading graph...")
graph: SkosGraph = load_graph_from_file("generated.graph")

print("Creating rdf skos string")
relation_search_index: RelationSearchIndex = RelationSearchIndex(graph)
to_skos_export(graph, relation_search_index, "example")
print("Done...")