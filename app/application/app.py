import json
from typing import Optional, List

from flask import Flask, request
from flask_cors import CORS

from application.order_utils import order_by_status
from graph.skos_graph import SkosGraph, RelationSearchIndex, NodeSearchIndex, SkosNode, SCHEMA_PREF_LABEL, \
    SCHEMA_TAXON_STATUS
from graph.skos_graph_utils import load_graph_from_file, search_node_start_with, \
    search_rec, get_hierarchy_upwards_from, order_by_name_length

print("Loading graph...")
graph: SkosGraph = load_graph_from_file("generated.graph")
print("Building relation indexes...")
relation_search_index: RelationSearchIndex = RelationSearchIndex(graph)
print("Building pref label node indexes...")
pref_label_node_search_index: NodeSearchIndex = NodeSearchIndex(graph)
print("Building descriptor node indexes...")
descriptor_node_search_index: NodeSearchIndex = NodeSearchIndex(graph, lambda x: x.descriptor)

app = Flask(__name__)
CORS(app)


@app.route("/search", methods=['GET'])
def get_search():
    search_term = request.args.get('term', type=str)
    result = search_node_start_with(graph, search_term.lower(), max_result_count=50)
    rsp = {
        "result": order_by_name_length(result)[:25]
    }
    return json.dumps(rsp, default=lambda o: o.__dict__)


@app.route("/related", methods=['GET'])
def get_related():
    descriptor = request.args.get('descriptor', type=str)
    depth = request.args.get('depth', type=int)

    node: Optional[SkosNode] = descriptor_node_search_index.get_nodes_for_key(descriptor)[0]
    if node is None:
        rsp = {
            "result": [],
            "hierarchy": []
        }
        return json.dumps(rsp, default=lambda o: o.__dict__)
    synonym_descriptors: List[str] = []
    search_rec(relation_search_index, node.descriptor, depth, synonym_descriptors)
    result = descriptor_node_search_index.get_all_nodes_for_keys(list(dict.fromkeys(synonym_descriptors)))
    rsp = {
        "result": order_by_status(result),
        "hierarchy": []
    }
    return json.dumps(rsp, default=lambda o: o.__dict__)


def filter_duplicates(hierarchy_unfiltered: List[SkosNode]):
    if len(hierarchy_unfiltered) == 0:
        return []
    filtered_hierarchy: List[SkosNode] = []
    node: SkosNode
    last_node: SkosNode = hierarchy_unfiltered[0]

    for node in hierarchy_unfiltered:
        if last_node.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal != node.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal \
                and node.get_attribute_by_schema(SCHEMA_TAXON_STATUS) != "sub_species":
            filtered_hierarchy.append(node)
        last_node = node

    return filtered_hierarchy


@app.route("/hierarchy", methods=['GET'])
def get_hierarchy():
    descriptor = request.args.get('descriptor', type=str)
    if descriptor is None:
        rsp = {
            "result": []
        }
        return json.dumps(rsp, default=lambda o: o.__dict__)
    hierarchy_unfiltered = get_hierarchy_upwards_from(descriptor, relation_search_index, descriptor_node_search_index)
    rsp = {
        "result": filter_duplicates(hierarchy_unfiltered)
    }
    return json.dumps(rsp, default=lambda o: o.__dict__)

app.run(port=1234, host="0.0.0.0")
