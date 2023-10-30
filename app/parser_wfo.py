import logging
import sys

from dwca.read import DwCAReader

from dwca_parser.parser_wfo import ParserWFO
from graph.skos_graph_utils import save_graph_to_file

logging.basicConfig(
    level=logging.INFO,
    format='%(threadName)10s %(name)18s: %(message)s',
    stream=sys.stderr,
)

dwca_file = DwCAReader("./taxa/WFO_Backbone.zip")
df = dwca_file.pd_read(dwca_file.descriptor.core.file_location)
graph = ParserWFO(df, "wfo.graph").process()
save_graph_to_file(graph, graph.name)