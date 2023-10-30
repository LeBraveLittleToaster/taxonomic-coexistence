import random
import time
from typing import List

from graph.skos_graph import SkosGraph, RelationSearchIndex, SCHEMA_SYNONYM, NodeSearchIndex, SkosNode, \
    default_pref_label_retriever
from graph.skos_graph_utils import load_graph_from_file

print("START")
g: SkosGraph = load_graph_from_file("old_generated.graph")

print("Building index")
relation_index: RelationSearchIndex = RelationSearchIndex(g)
node_index: NodeSearchIndex = NodeSearchIndex(g)

search_node: SkosNode = random.choice(g.nodes)


def search_rec(s_index: RelationSearchIndex, descriptor: str, depth: int, result: List[str]) -> None:
    if depth <= 0:
        return
    next_descriptors: List[str] = s_index.get_all_descriptor_for_descriptor(descriptor, SCHEMA_SYNONYM)
    result += next_descriptors
    for desc in next_descriptors:
        search_rec(s_index, desc, depth - 1, result)


start = time.time()

r: List[str] = []
search_rec(relation_index, search_node.descriptor, 5, r)
r = list(dict.fromkeys(r))
end = time.time()
print("Search took: " + str(end - start))
print(r)

search_pref_label: str = default_pref_label_retriever(search_node)
print(search_pref_label)
print(node_index.get_nodes_for_key(search_pref_label))
