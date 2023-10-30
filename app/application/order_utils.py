from collections import defaultdict
from typing import List, Optional

from graph.skos_graph import SkosNode, SCHEMA_TAXON_STATUS

default_mapping_key = "deff"
simple_order: List[str] = ["accepted", "Accepted", "valid", "Synonym", "synonym"]


def order_by_status(nodes: List[SkosNode]) -> List[SkosNode]:
    status_mapping: defaultdict = defaultdict(lambda: [])
    node: SkosNode
    for node in nodes:
        status: Optional[str] = node.get_attribute_by_schema(SCHEMA_TAXON_STATUS).literal
        if status is None or status not in simple_order:
            status_mapping[default_mapping_key].append(node)
        else:
            status_mapping[status].append(node)
    ordered_result: List[SkosNode] = []
    status: str
    for status in simple_order:
        ordered_result += status_mapping[status]
    ordered_result += status_mapping[default_mapping_key]
    return ordered_result
