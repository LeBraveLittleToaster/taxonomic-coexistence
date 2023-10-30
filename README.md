# Quick Start Guide

The goal of the project is to provide a simple, yet powerful system to preprocess, link and serve botanical taxonomic data. This is achieved by a preprocessing stage consisting of a parser and merger script as well as a flask/react.js based web application.

> Software Versions

* Backend: `Python 3.9.x`, refer to the `/app/application/requirements.txt` for additional framework versions
* Frontend: `Node v16.7.0`

> Hardware Requirements

* recommended 32GB RAM
* x86 tested, ARM32 + ARM64 not tested but should work as well

## Quickstart webapp

* Clone the repository, either download the prebuild `generated.graph` (to large for git) and place it in `/app/application` folder or run the merger script as described in the merger section
* Install the needed Python version (see above) and install the requirements via the requirement files

  ```
  python -m pip install -r requirements.txt
  ```
* Run the backend script via

  ```
  cd app/ && python ./application/app.py
  ```
* Install the frontend dependencies via

  ```
  cd /react-app/frontend && npm install (only once needed)
  ```
* Run the frontend script

  ```
  cd /react-app/frontend && npm start
  ```
* The webapp should now be available under the link (default: http://localhost:5000)

## Quickstart preprocessing and Skos export

* Clone the repository. Install the needed Python version (see above) and install the requirements via the requirement files

  ```
  python -m pip install -r requirements.txt
  ```
* Run the parser script to obtain the `itis.graph`,`tpl.graph` and `wfo.graph` files. The script expect thre Darwin Core Archieve files (itis.zip, tpl.zip, WFO_Backbone.zip) located in the `/app/taxa/` folder. The `parser_main.py` script will run all parsers asynchronous.

  ```
  cd app && python parser_main.py
  ```

  Alternatively, it is possible to run the individual parsers separately.

  ```
  cd app && python parser_itis.py
  ```

  ```
  cd app && python parser_tpl.py  
  ```

  ```
  cd app && python parser_wfo.py
  ```
* Run the merger script to obtain the `generated.graph` file. The script expects three files (itis.graph, tpl.graph, wfo.graph) produced by the parsers, located in the same `/app/application/` folder.

  ```
  cd app/ && PYTHONPATH=$(pwd) python ./application/merger.py
  ```
* Run the exporter script to obtain the skos `out.ttl` file.

  ```
  cd app/ && PYTHONPATH=$(pwd) python ./application/SkosExport.py
  ```

> Note: The exporter provides no status update. The process can take more then half an hour even on powerful hardware.

## Quickstart skosify

[Skosify](https://github.com/NatLibFi/Skosify) is a tool to validate and enhance SKOS vocabularies.

Skosify divides his output in warnings and errors. Errors are crucial problems which should be fixed, while warnings are minor suggestions.

* Install [skosify](https://pypi.org/project/skosify/) with the following command

  ```
  pip install --upgrade skosify
  or
  python -m pip install --upgrade skosify
  depending on your OS
  ```
* Clone the repository and place the, from the exporter created `out.ttl` in the `/app/application/` folder. After that run the following command

  ```
  cd app/ && PYTHONPATH=$(pwd) python ./application/skosify_runner.py
  ```

> The script can run more then an hour! Skosify online outputs

## Known issues

* In e.g. linux, the preinstalled python as accessed by the *python3* keyword. If you need to use *python3* or other aliases like *python* or *py* depends on your local python installation.
* IDEs like PyCharm move the python root folder automatically to the project root. On console this could lead to the "graph" module not beeing recognized. A solution is to tell python explicitly where the project root is located. <br>E.g.:

  ```
  PYTHONPATH=$(pwd) python /application/merger.py
  ```

# Documentation

The following picture describes the overall pipeline and steps involved.

![Classes](/ressource/Pipeline.drawio.png)

> Blue are scripts, which are described below, yellow are files which are needed or produced

## Preprocessing

This prototype can utilize data dumps from "The plant list", "ITIS" and "World Flora Online". A dump is provided outside the repository. Future data dumps can vary in format, depending on the data provider. If you are not sure, use the already merged dump in the same cloudstore.<br> As described in the paper, the data is first converted into a custom build data format.

## Data format

The parser, merger, export as well as the web application are all build around the *SkosGraph* class, located in `/app/graph/skos_graph.py`. This class, combined with the *SkosNode*, *SkosRelation* and *SkosAttribute* (same file), represent the data encoded in the graph. <br>

At its core, the data structure consists of the following classes:

* **SkosGraph**, represents a whole graph hierarchy, stores all nodes and relations
* **SkosNode**, represents one taxonomic entry in the graph, contains attributes
* **SkosRelation**, links two nodes by descriptor
* **SkosAttribute**, represents an attribute for a node

![Classes](/ressource/Classes.png)

> Entities provided in the system and its attributes.

In this setup, the descriptor field (or id field) needs to be unique to ensure correct linking via the *SkosRelation* class between to nodes (identified by the descriptor).

While the *SkosGraph* can store already created SkosNodes and SkosRelations, a wide range of utility methods are provided for the use in the botanical context. These methods add domain specific schemas to the respective relations.

```
# creating SkosGraph instance
graph: SkosGraph = SkosGraph()

# add kingdom with name "KingdomName1" and descriptor (id) "k1"
graph.add_kingdom_node("k1", "KingdomName1")

# add familiy with name "FamilyName1" and descriptor (id) "f1"
graph.add_family_node("f1", "FamilyName1")
# create inheritance relation from family to kingdom by descriptor
graph.add_family_to_kingdom("f1", "k1")

# adding genus
graph.add_genus_node("g1", "GenusName1")
graph.add_genus_node("g2", "GenusName2")
graph.add_genus_to_family("g1", "f1")
graph.add_genus_to_family("g2", "f1")

# adding species
graph.add_species_node("s1", "SpeciesName1")
graph.add_species_node("s2", "SpeciesName2")
graph.add_species_to_genus("s1", "g1")
graph.add_species_to_genus("s2", "g1")

# Adding a synonym relation between species s1 and s2
graph.add_synonym_relation("s1", "s2")
```

> Example can be found under `/test/rsc/test_skos_graph.py`

Further more, the `/app/graph/skos_graph_utils.py` script provides a wide range of utility methods. They are mostly used by the web application e.g. search functionality

```
search_node_start_with(graph, "SearchWord", max_result_count=50)
```

Or get the hierarchy for an provided descriptor upwards

```
get_node_hierarchy_upwards_from(graph, "descriptor")
```

### Parser

Data is provided in a hierarchical format by the data sources. The parser uses a recursive approach to collect all data from the Darwin Core files and translate them to our tree structure. A parser section located at `/app/dwc_parser`, containing a parser base and three implementations for each data source.

* `parser_base.py` - base parser, shared by all implementations
* `parser_tpl.py` - parser for the Plant List
* `parser_itis.py` - parser for the Integrated Taxonomic Integration System
* `parser_wfo.py` - parser for World Flora Online

The parser stage exports the result in three ".graph" files, which are python objects serialized as binary via the framework [pickle](https://docs.python.org/3/library/pickle.html).

To parse other taxonomies, it may be necessary to implement a new parser class that inherits from `parser_base.py`.

### Search Index

A *search index* is a cache like structure which extracts the ids and relations to a dictionary structure. This enables us to query the dictionary descriptors instead querying the whole objects.

> These indexes implementation can be found under `/app/graph/skos_graph.py#RelationSearchIndex`.

### Merger

The merger creates one graph file out of the the three graph files provided by the Parser stage. On how to run the merger, refer to the quick start section.<br> The procedure simply compares name by name all three taxonomy entries and creates an edge for all synonyms.

> As output you get a graph as well. The default name for the graph export is `generated.graph` with the same binary format as the inputs.

### SkosExport

The `/app/application/SkosExport.py` script serializes the `generated.graph` to a `out.ttl` file containing the same graph serialized as string (skos-turtle-format). While the *SkosExport* script executes all necessary steps, the main logic is stored in `/app/application/MultiThreadExport.py`.As the name suggest, the export is computed on different threads. Storing the whole exported string in memory takes currently around 7GB of RAM. If greater amount of data should be computed in the future, this script should be adjusted, so that each thread stores their result to a file, which is later combined to one file, instead of storing all results in RAM.

Due to the graph structure, the export is achieved by iterating through the nodes and aggregate all attributes to a RDF-turtle string. Additionally, hardcoded headers with the used terminology are added to the file.

> Exports a `out.ttl` file containing the rdf-turtle string. This file is formatted and human readable.

## Subsystem WebApp

The web application backend is located under the `/app/application` directory as well.

The implementation is straight forward. The following API is provided by a flask based webserver, found in `/app/application/app.py`. Before the flask server is running, the script loads the graph from the `generated.graph` file, which need be located in the same directory. For installation instruction see above in the Quick Start paragraph.

### API

* `/search?term=?` - string match search
* `/related?descriptor=?&depth=?` - search for related items to node for given descriptor, the depth is the search depth described in the paper
* `/hierarchy?descriptor=?` - taxonomic hierarchy for an item identified by the descriptor

### React

The frontend is build with [react.js](https://reactjs.org/). The app is located under `/react-app/frontend/`.

Basically, the application consists of two major files, `/src/App.tsx` and `/src/PlantDetail.tsx`.

The *App class* contains the search and overall layout, while the *PlantDetail* represents the synonym and hierarchy windows. Both components are written in a functional style, based on [useState](https://reactjs.org/docs/hooks-state.html) to represent state data. For loading data, we use the standard [fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) API. Styling is done with CSS.

## Important files

* For context, please read the corresponding paper.
* If you don´t want to run it yourself, you can find the skosify output (23.10.2022) under `/ressource/SkosifyOutput.txt`
* You can find the Abstract and Assignment context in `/ressource/Abstract-Kooperation.pdf` and `/ressource/Assignment.pdf`
