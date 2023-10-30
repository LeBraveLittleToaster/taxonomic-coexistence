import asyncio
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dwca.read import DwCAReader
from pandas import DataFrame

from dwca_parser.parser_itis import ParserITIS
from dwca_parser.parser_tpl import ParserTPL
from dwca_parser.parser_wfo import ParserWFO
from graph.skos_graph import SkosGraph
from graph.skos_graph_utils import save_graph_to_file

_DEFAULT_KINGDOM = "PLANTAE"
NAME_TPL = "tpl.graph"
NAME_WFO = "wfo.graph"
NAME_ITIS = "itis.graph"

class Parser(object):
    PATH = "./taxa/"
    FILE_NAMES = {
        NAME_TPL: "tpl.zip",
        NAME_WFO: "WFO_Backbone.zip",
        NAME_ITIS: "itis.zip"
    }
    dataframes: dict[str, DataFrame] = {}
    graphes: dict[str, SkosGraph] = {}

    def __init__(self, target_kingdoms=None, **additional_file_paths) -> None:
        for key, value in additional_file_paths.items():
            self.FILE_NAMES[key] = value
        self.__load_dwca()
        self.__create_skos_graphs(target_kingdoms)

    def __load_dwca(self) -> None:
        for key, filename in self.FILE_NAMES.items():
            dwca_file: DwCAReader = DwCAReader(self.PATH + filename)
            self.dataframes[key] = dwca_file.pd_read(dwca_file.descriptor.core.file_location)

    def __create_skos_graphs(self, target_kingdoms):
        logging.basicConfig(
            level=logging.INFO,
            format='%(threadName)10s %(name)18s: %(message)s',
            stream=sys.stderr,
        )
        executor = ThreadPoolExecutor(max_workers=3)
        event_loop = asyncio.get_event_loop()
        try:
            res: List[SkosGraph] = event_loop.run_until_complete(self.__run_async_parses(executor))
            for graph in res:
                save_graph_to_file(graph, graph.name)
        finally:
            event_loop.close()

    async def __run_async_parses(self, executor):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, ParserTPL(self.dataframes[NAME_TPL], NAME_TPL).process),
            loop.run_in_executor(executor, ParserITIS(self.dataframes[NAME_ITIS], NAME_ITIS).process),
            loop.run_in_executor(executor, ParserWFO(self.dataframes[NAME_WFO], NAME_WFO).process)
        ]
        completed, pending = await asyncio.wait(tasks)
        results = [t.result() for t in completed]
        return results
