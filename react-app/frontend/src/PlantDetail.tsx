import makeStyles from '@material-ui/core/styles/makeStyles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Card from '@material-ui/core/Card';
import { BASE_URL, keyAuthor, keyDefinition, keyHistoryNote, keyInScheme, keyPrefLabel, Plant, PlantResponse } from './App';
import { CircleLoader } from 'react-spinners';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import { useEffect, useState } from 'react';
import { convertToPlants } from "./App"
import { responsiveFontSizes } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
  container: {
    display: "flex",
    justifyContent: "center",
    width: "100%"
  },
  searchPanel: {
    flex: 1,
    textAlign: "center",
    display: "flex",
    flexDirection: "column",
  },
  noFound: {
    display: "flex",
    width: "100%",
    alignItems: "start",
    padding: "25px"
  },
  list: {
    overflow: "auto",
    flex: 1,
    maxHeight: "85%"
  },
  listItem: {
    paddingLeft: "50px",
    display: "flex",
    justifyContent: "space-between"
  },
  termForm: {
    margin: "50px"
  },
  loaderContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100px",
    minWidth: "100px"
  },
  headerTextContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "start",
    padding: "25px"
  },
  headerText: {
    fontSize: "3em",
    fontWeight: "bold"
  },
  headerTextHierarchy: {
    fontSize: "3em",
    fontWeight: "bold"
  },
  plantNameText: {
    fontSize: "1.6em",
    fontWeight: "bold"
  },
  hierarchyContainer: {
    minWidth: "300px",
    height: "100%",
  },
  horizontalWrapper: {
    display: "flex",
    width: "100%",
    height: "100%",
    flexDirection: "row",
    alignItems: "stretch"
  },
  hierarchyPrefLabel: {
    fontSize: "1.5em",
    marginRight: "25px"
  },
  synonymColumn: {
    flexGrow: 5,
    height: "100%"
  },
  hierarchyColumn: {
    flexGrow: 1
  },
  loadHierarchyText : {
    
  }
}));


type PlantDetailProps = {
  response: PlantResponse[] | null | undefined,
  selectedPlant: Plant | undefined,
}

type VisualPlant = {
  descriptor: string,
  prefLabel: string,
  inScheme: string,
  historyNote: string,
  definition: string,
  author: string
}

function PlantDetail({ selectedPlant, response }: PlantDetailProps) {

  const [hierarchy, setHierarchy] = useState<VisualPlant[] | undefined>(undefined);
  const [selectedSynonym, setSelectedSynonym] = useState<Plant | undefined>(undefined);

  function handleHierarchyButton(e: any, plant: Plant) {
    setHierarchy([])
    setSelectedSynonym(plant);
    e.preventDefault();
    fetch("http://" + BASE_URL + ":1234/hierarchy?descriptor=" + plant.descriptor + "&depth=2")
      .then(res => res.json())
      .then(
        (msg) => {
          setHierarchy(undefined)
          let response: VisualPlant[] = convertToPlants(msg.result);
          console.log("HIERARCHY:")
          console.log(response)
          setHierarchy(response.reverse())
        }
        ,
        (error) => {
          console.log(error)
          setHierarchy([])
        }
      )
  }

  const plants: VisualPlant[] = response === undefined ? [] : response === null ? [] : (response?.map((e: PlantResponse) => {
    return {
      descriptor: e.descriptor ?? "",
      prefLabel: e.attributes.find(a => a.schema == keyPrefLabel)?.literal ?? "",
      inScheme: e.attributes.find(a => a.schema == keyInScheme)?.literal ?? "",
      historyNote: e.attributes.find(a => a.schema == keyHistoryNote)?.literal ?? "",
      definition: e.attributes.find(a => a.schema == keyDefinition)?.literal ?? "",
      author: e.attributes.find(a => a.schema == keyAuthor)?.literal ?? ""
    }
  }))

  const classes = useStyles();
  return (
    <div className={classes.container}>
      {response === null ? <div /> :
        <div className={classes.searchPanel}>

          <div className={classes.horizontalWrapper}>
            <div className={classes.synonymColumn}>
              <div className={classes.headerTextContainer}>

                <a className={classes.headerText}>Synonyms</a>
                <a className={classes.plantNameText}> {(selectedPlant?.prefLabel ?? "") + " as " + (selectedPlant?.inScheme ?? "") + " | status: " + (selectedPlant?.definition ?? "")} [{selectedPlant?.historyNote ?? ""}]</a>

              </div>
              <List className={classes.list}>
                {response === undefined ?
                  <div className={classes.loaderContainer}>
                    <CircleLoader size={50}></CircleLoader>
                  </div>
                  : <div>
                    {
                      plants.length == 0 ?
                        <div className={classes.noFound}><a>No synonyms found</a></div>
                        : plants.map((p: VisualPlant, i: number) =>
                          <ListItem className={classes.listItem} key={i} selected={selectedSynonym?.descriptor === p.descriptor} onClick={(e) => handleHierarchyButton(e, p)}>
                            <ListItemText
                              primary={p.prefLabel}
                              secondary={p.inScheme + " in " + p.historyNote + " | status: " + p.definition + (p.author === undefined || p.author.length == 0 ? "" : " | author: " + p.author)} />
                          </ListItem>
                        )
                    }</div>}
              </List>
            </div>
            <div className={classes.hierarchyColumn}>
              <div className={classes.hierarchyContainer}>
                <div className={classes.headerTextContainer}>

                  <a className={classes.headerTextHierarchy}>Hierarchy</a>
                  
                </div>
                <List>
                  {
                    <a className={classes.loadHierarchyText}>{hierarchy == undefined ? "Click on synonym to load" : ""}</a>
                  }
                  {
                    hierarchy?.map((r: VisualPlant, i) => {
                      return (
                        <ListItem className={classes.listItem} key={i}>
                          <a className={classes.hierarchyPrefLabel}>{r.prefLabel}</a>
                          <a>{r.inScheme}</a>
                        </ListItem>);
                    })
                  }
                </List>
              </div>
            </div>
          </div>

        </div>
      }
    </div >
  );
}

export default PlantDetail;
