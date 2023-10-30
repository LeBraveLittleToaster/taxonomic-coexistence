import { useState } from 'react';
import TextField from '@material-ui/core/TextField';
import makeStyles from '@material-ui/core/styles/makeStyles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import SearchIcon from '@material-ui/icons/Search';
import PlantDetail from './PlantDetail';
import { CircleLoader } from 'react-spinners';
import { Button } from '@material-ui/core';

export const keyPrefLabel = "skos:prefLabel"
export const keyInScheme = "skos:inScheme"
export const keyHistoryNote = "skos:historyNote"
export const keyDefinition = "skos:definition"
export const keyAuthor = "skos:scopeNote"

export const BASE_URL = "localhost"

const useStyles = makeStyles((theme) => ({
  pageContainer: {
    display: "flex",
    alignContent: "left",
    height: "100vh"
  },
  sidebar: {
    display: "flex",
    minWidth: "400px"
  },
  searchPanel: {
    textAlign: "center",
    display: "flex",
    flexDirection: "column",
    flex: 1
  },
  searchField: {
    padding: "25px",
  },
  list: {

  },
  listItem: {

  },
  scrollarea: {
    overflowY: "auto",
    overflowX: "hidden",
    height: "100%",
    width: "100%"
  },
  loaderContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100px",
    minWidth: "100px"
  },
  noResultTxt: {
    display: "flex",
    flexDirection: "column"
  },
  searchButton: {
    marginTop: "20px",
    width: "100%"
  },
}));

export type AttributeResponse = {
  schema: string,
  literal: string
}
export type PlantResponse = {
  descriptor: string,
  attributes: AttributeResponse[]
}

export type Plant = {
  descriptor: string,
  prefLabel: string,
  inScheme: string,
  historyNote: string,
  definition: string,
  author: string
}

export const convertToPlants = (result: any) => {
  let plants: Plant[] = []
  result.forEach((e: any) => {
    let descriptor: string = e.descriptor;
    let prefLabel: string = e.attributes.find((a: any) => a.schema == keyPrefLabel).literal;
    let inScheme: string = e.attributes.find((a: any) => a.schema == keyInScheme).literal;
    let historyNote: string = e.attributes.find((a: any) => a.schema == keyHistoryNote).literal;
    let definition: string = e.attributes.find((a: any) => a.schema == keyDefinition).literal;
    let author: string = e.attributes.find((a: any) => a.schema == keyAuthor).literal;
    plants.push({
      descriptor: descriptor,
      prefLabel: prefLabel,
      inScheme: inScheme,
      historyNote: historyNote,
      definition: definition,
      author: author
    })
  })
  console.log("FOUND PLANTS:")
  console.log(plants)
  return plants;
}

function App() {
  const classes = useStyles();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResult] = useState<Plant[] | undefined>([]);
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedPlant, setSelectedPlant] = useState<Plant | undefined>(undefined);
  const [plantResponse, setPlantResponse] = useState<PlantResponse[] | undefined | null>(null);

  function handleSubmit(event: any) {
    event.preventDefault();
    console.log(searchTerm)
    setIsLoading(true);
    fetch("http://" + BASE_URL + ":1234/search?term=" + searchTerm)
      .then(res => res.json())
      .then(
        (msg) => {
          console.log(msg)
          setResult(convertToPlants(msg.result))
        }
        ,
        (error) => console.log(error)
      ).finally(() => setIsLoading(false))
  }

  function handleOnItemClick(e: any, plant: Plant) {
    e.preventDefault();
    setPlantResponse(undefined)
    setSelectedPlant(undefined)
    fetch("http://" + BASE_URL + ":1234/related?descriptor=" + plant.descriptor + "&depth=2")
      .then(res => res.json())
      .then(
        (msg) => {
          let response: PlantResponse[] = msg.result;
          setPlantResponse(response);
          setSelectedPlant(plant)
        }
        ,
        (error) => console.log(error)
      )
  }
  return (
    <div className={classes.pageContainer}>
      <div className={classes.sidebar}>
        <div className={classes.searchPanel}>
          <form className={classes.searchField} onSubmit={handleSubmit} >
            <TextField
              fullWidth
              id="outlined-number"
              label="Search Term"
              type="text"
              variant="outlined"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
            <Button
              variant="contained"
              className={classes.searchButton}
              startIcon={<SearchIcon />}
              onClick={handleSubmit}
            >
              Search
            </Button>
          </form>
          <div className={classes.scrollarea}>
            {isLoading ?
              <div className={classes.loaderContainer}>
                <CircleLoader size={50}></CircleLoader>
              </div> :
              <div>
                {results !== undefined && results.length !== 0 ?
                  <List className={classes.list}>
                    {results.map((r: Plant, i) => {
                      let header = r.prefLabel + " (" + r.historyNote + ")"
                      return (
                        <ListItem className={classes.listItem} key={i} selected={selectedPlant?.descriptor == r.descriptor} onClick={(e) => handleOnItemClick(e, r)} >
                          <ListItemText primary={header} secondary={r.inScheme + " | " + r.definition + (r.author === undefined || r.author.length == 0 ? "" : " | " + r.author)} />
                        </ListItem>)
                    }
                    )}
                  </List>
                  : <div className={classes.noResultTxt}><a>No Results - insert new search term</a><a>---</a><a>Press Search or "Enter" to submit</a></div>
                }
              </div>
            }
          </div>
        </div>
      </div>
      <PlantDetail selectedPlant={selectedPlant} response={plantResponse} />
    </div>
  );
}

export default App;
