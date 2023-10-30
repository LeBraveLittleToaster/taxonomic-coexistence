import pickle
from typing import Optional, List

from graph.skos_graph import SkosGraph, SkosNode, SkosRelation, SCHEMA_NARROWER, SCHEMA_PREF_LABEL, SkosAttribute, \
    SCHEMA_HISTORY_NOTE, SCHEMA_SYNONYM, NodeSearchIndex, RelationSearchIndex


def get_parent_node(graph: SkosGraph, child_descriptor: str) -> Optional[SkosNode]:
    node_opt: Optional[SkosNode] = graph.get_node_by_descriptor(child_descriptor)
    if node_opt is None:
        return None
    out_relations: [SkosRelation] = graph.get_outgoing_relations_with_descriptor(node_opt.descriptor)
    if out_relations is None:
        return None
    to_parent_relation: Optional[SkosRelation] = next((x for x in out_relations if x.label is SCHEMA_NARROWER), None)
    if to_parent_relation is None:
        return None
    return graph.get_node_by_descriptor(to_parent_relation.end_descriptor)


def get_node_hierarchy_upwards_from(graph: SkosGraph, descriptor: str, max_search_depth: int = 10) -> [SkosNode]:
    cur_node_opt: Optional[SkosNode] = graph.get_node_by_descriptor(descriptor)

    if cur_node_opt is None:
        return []

    parent_nodes: [SkosNode] = []
    for i in range(0, max_search_depth):
        parent_node: Optional[SkosNode] = get_parent_node(graph, cur_node_opt.descriptor)
        if cur_node_opt is not None:
            parent_nodes.append(cur_node_opt)
        cur_node_opt = parent_node
        if parent_node is None:
            return parent_nodes

    return parent_nodes


def __is_start_end_schema_correct(relation: SkosRelation, start_descriptor: str, end_descriptor: str,
                                  schema_filter: [str]) -> bool:
    relation_direction_correct = relation.start_descriptor is start_descriptor and relation.end_descriptor is end_descriptor
    if relation_direction_correct and len(schema_filter) == 0:
        return True
    return relation_direction_correct and relation.label in schema_filter


def get_relations_with_schema(graph: SkosGraph, start_descriptor: str, end_descriptor: str, schema_filter: [str]) -> \
        [SkosRelation]:
    relation: SkosRelation
    return [relation for relation in graph.relations if
            __is_start_end_schema_correct(start_descriptor, end_descriptor, schema_filter)]


def search_node_start_with(graph: SkosGraph, search: str, max_result_count: int = 25) -> List[SkosNode]:
    result: List[SkosNode] = []
    node: SkosNode
    for node in graph.nodes:
        label: SkosAttribute
        label = node.get_attribute_by_schema(SCHEMA_PREF_LABEL)
        if label is not None and label.literal.lower().startswith(search):
            result.append(node)
        if len(result) >= max_result_count:
            return result
    return result


def get_order_key(node: SkosNode):
    return len(node.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal)


def order_by_name_length(nodes: List[SkosNode]):
    nodes.sort(key=get_order_key)
    return nodes


def save_graph_to_file(graph: SkosGraph, file_path: str):
    with open(file_path, 'wb+') as f:
        graph_as_bytes = pickle.dumps(graph)
        f.write(graph_as_bytes)
        f.close()


def load_graph_from_file(file_path) -> Optional[SkosGraph]:
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            f.close()
            return pickle.loads(data)
    except Exception:
        return None


def load_test_graph() -> Optional[SkosGraph]:
    return load_graph_from_file("./rsc/test_out.graph")


def get_descriptor_for_name(name: str, graph: SkosGraph) -> [SkosNode]:
    nodes: [SkosNode] = []
    node: SkosNode
    for node in graph.nodes:
        name_of_node = node.get_attribute_by_schema(SCHEMA_PREF_LABEL)
        if name_of_node is not None and name_of_node == name:
            nodes.append(node)
    return nodes


def get_relations_containing_descriptor_filtered(graph: SkosGraph, descriptor: str, label_filter_include: List[str]) -> \
        List[SkosRelation]:
    relations: List[SkosRelation] = []
    relation: SkosRelation
    for relation in graph.relations:
        if relation.start_descriptor == descriptor or relation.end_descriptor == descriptor:
            if relation.label in label_filter_include:
                relations.append(relation)
    return relations


def get_synonym_nodes(graph: SkosGraph, descriptor: str) -> List[str]:
    synonym_descriptors: List[str] = []
    relation: SkosRelation
    for relation in graph.relations:
        if relation.label == SCHEMA_SYNONYM:
            if relation.start_descriptor == descriptor:
                synonym_descriptors.append(relation.end_descriptor)
            if relation.end_descriptor == descriptor:
                synonym_descriptors.append(relation.start_descriptor)
    return synonym_descriptors


def merge_graphs(graph_itis: SkosGraph, graph_tpl: SkosGraph, graph_wfo: SkosGraph) -> SkosGraph:
    graph: SkosGraph = SkosGraph("merged graph")
    search_index_tpl: NodeSearchIndex = NodeSearchIndex(graph_tpl)
    search_index_itis: NodeSearchIndex = NodeSearchIndex(graph_itis)
    search_index_wfo: NodeSearchIndex = NodeSearchIndex(graph_wfo)
    node_tpl: SkosNode
    node_itis: SkosNode
    node_wfo: SkosNode

    node_synonym: SkosNode

    print("Adding tpl nodes history note")
    for node_tpl in graph_tpl.nodes:
        node_tpl.add_attribute(SCHEMA_HISTORY_NOTE, "tpl")
    print("Adding itis nodes history note")
    for node_itis in graph_itis.nodes:
        node_itis.add_attribute(SCHEMA_HISTORY_NOTE, "itis")
    print("Adding wfo nodes history note")
    for node_wfo in graph_wfo.nodes:
        node_wfo.add_attribute(SCHEMA_HISTORY_NOTE, "wfo")

    print("Matching itis to tpl...")
    for node_itis in graph_itis.nodes:
        node_itis_pref_label: Optional[str] = node_itis.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal
        node_tpl: Optional[List[SkosNode]] = search_index_tpl.get_nodes_for_key(node_itis_pref_label)
        if node_tpl is not None:
            for node_synonym in node_tpl:
                graph.add_synonym_relation(node_synonym.descriptor, node_itis.descriptor)

    print("Matching itis to wfo...")
    for node_itis in graph_itis.nodes:
        node_itis_pref_label: Optional[str] = node_itis.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal
        node_wfo: Optional[List[SkosNode]] = search_index_wfo.get_nodes_for_key(node_itis_pref_label)
        if node_wfo is not None:
            for node_synonym in node_wfo:
                graph.add_synonym_relation(node_synonym.descriptor, node_itis.descriptor)

    print("Matching tpl to wfo...")
    for node_tpl in graph_tpl.nodes:
        node_tpl_pref_label: Optional[str] = node_tpl.get_attribute_by_schema(SCHEMA_PREF_LABEL).literal
        node_wfo: Optional[List[SkosNode]] = search_index_wfo.get_nodes_for_key(node_tpl_pref_label)
        if node_wfo is not None:
            for node_synonym in node_wfo:
                graph.add_synonym_relation(node_synonym.descriptor, node_tpl.descriptor)

    print("Adding tpl nodes")
    for node_tpl in graph_tpl.nodes:
        graph.nodes.append(node_tpl)
    print("Adding wfo nodes")
    for node_wfo in graph_wfo.nodes:
        graph.nodes.append(node_wfo)
    print("Adding itis nodes")
    for node_itis in graph_itis.nodes:
        graph.nodes.append(node_itis)

    relation_tpl: SkosRelation
    relation_itis: SkosRelation
    relation_wfo: SkosRelation
    print("Copying old tpl relations")
    for relation_tpl in graph_tpl.relations:
        graph.relations.append(relation_tpl)
    print("Copying old itis relations")
    for relation_itis in graph_itis.relations:
        graph.relations.append(relation_itis)
    print("Copying old wfo relations")
    for relation_wfo in graph_wfo.relations:
        graph.relations.append(relation_wfo)

    return graph


def search_rec(s_index: RelationSearchIndex, descriptor: str, depth: int, result: List[str]) -> None:
    if depth <= 0:
        return
    next_descriptors: List[str] = s_index.get_all_descriptor_for_descriptor(descriptor, SCHEMA_SYNONYM)
    result += next_descriptors
    for desc in next_descriptors:
        search_rec(s_index, desc, depth - 1, result)


def get_hierarchy_upwards_from(descriptor: str, relation_search_index: RelationSearchIndex,
                               descriptor_node_search_index: NodeSearchIndex) -> List[SkosNode]:
    i: int = 0
    result: List[str] = [descriptor]
    relation: Optional[SkosRelation] = relation_search_index.get_broader_or_synonym_relation(
        descriptor, descriptor_node_search_index)
    while relation is not None:
        result.append(relation.start_descriptor)
        relation = relation_search_index.get_broader_or_synonym_relation(
            relation.start_descriptor,
            descriptor_node_search_index)
        if i > 25:
            return []
        i += 1
    return descriptor_node_search_index.get_all_nodes_for_keys(result)
