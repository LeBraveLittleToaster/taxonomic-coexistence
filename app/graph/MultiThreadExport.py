# -*- coding: utf-8 -*-
import concurrent.futures
import sys

from graph.skos_graph import SkosGraph, SkosNode, SkosAttribute, SCHEMA_IN_SCHEME, SkosRelation, RelationSearchIndex


def to_rdf_skos_str(domain_name: str, nodes: [SkosNode], edge_lookup: RelationSearchIndex) -> str:
    out = ""

    node: SkosNode
    for node in nodes:
        out += domain_name + ":" + str(node.descriptor) + " rdf:type skos:Concept;\n"
        lines_out = []
        attribute: SkosAttribute

        for attribute in node.attributes:
            lit = str(attribute.literal).translate(str.maketrans({"-":  "",
                                                                  '"': ""}))
            if attribute.schema != SCHEMA_IN_SCHEME:
                lines_out.append('  ' + attribute.schema + ' "' + lit + '"')
            else:
                lines_out.append('  ' + attribute.schema + ' ' + domain_name + ':' + lit)

        relation: SkosRelation
        for relation in edge_lookup.forward_relation_dict[node.descriptor]:
            lines_out.append('  ' + relation.label + ' ' + domain_name + ':' + relation.end_descriptor + '')

        for i in range(0, len(lines_out)):
            out += lines_out[i]
            if i == len(lines_out) - 1:
                out += ".\n\n"
            else:
                out += ";\n"
    return out


def to_skos_export(graph: SkosGraph, edge_lookup: RelationSearchIndex, domain_name: str):
    out = ""
    out += "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    out += "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n"
    out += "@prefix example: <http://www." + domain_name + ".com/> .\n\n"
    out += domain_name + ':kingdom rdf:type skos:ConceptScheme; skos:prefLabel "kingdom" .\n'
    out += domain_name + ':family rdf:type skos:ConceptScheme; skos:prefLabel "family" .\n'
    out += domain_name + ':species rdf:type skos:ConceptScheme; skos:prefLabel "species" .\n'
    out += domain_name + ':genus rdf:type skos:ConceptScheme; skos:prefLabel "genus" .\n'

    sys.stdout.write("START SLICING...")


    nodes_slices: [[SkosNode]] = []
    node: SkosNode
    i: int = 0
    cur_slice: [SkosNode] = []
    for node in graph.nodes:
        cur_slice.append(node)
        i += 1
        if i >= 100000:
            nodes_slices.append(cur_slice)
            cur_slice = []
            i = 0
    print("done")
    sys.stdout.write("BUILD CONCURRENT THREADS...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(to_rdf_skos_str, domain_name, nodes, edge_lookup) for nodes in nodes_slices]
        print("done")
        sys.stdout.write("START CONCURRENT THREADS...")
        results = [f.result() for f in futures]
    print("done")

    sys.stdout.write("START WRITING TO FILE...")
    with open("out.ttl", "w+", encoding="utf-8") as f:
        f.write(out)
        for r in results:
            f.write(r)
        f.close()
    print("done")
    print("EXPORT FINISHED!")
