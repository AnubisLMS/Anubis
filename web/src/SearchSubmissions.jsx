import React, {useState} from "react";
import {Redirect} from "react-router-dom";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import InputAdornment from "@material-ui/core/InputAdornment";
import SearchIcon from "@material-ui/icons/Search";
import Button from "@material-ui/core/Button";
import {makeStyles} from "@material-ui/core/styles";


const useStyles = makeStyles(theme => ({
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  card: {
    marginBottom: theme.spacing(2),
  },
  searchButton: {
    margin: theme.spacing(1)
  },
}));


export default function SearchSubmissions() {
  const classes = useStyles();
  const [commit, setCommit] = useState('');
  const [search, setSearch] = useState(false);

  const searchbar = (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h6'} gutterBottom>
          Search for a submission
        </Typography>
        <Grid
          container
          direction={"row"}
          align={'center'}
          justify={'center'}
        >
          <Grid item xs={12} sm={10}>
            <TextField
              required
              autoFocus
              fullWidth
              variant={'outlined'}
              label={'commit hash'}
              InputProps={{
                startAdornment: <InputAdornment position="start"><SearchIcon/></InputAdornment>,
              }}
              onChange={e => setCommit(e.target.value.trim())}
              onKeyPress={e => e.key === 'Enter' ? setSearch(true) : null}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Button
              variant={"contained"}
              color={"primary"}
              className={classes.searchButton}
              onClick={() => setSearch(true)}
            >
              Search
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  if (search) {
    setTimeout(() => setSearch(false), 0);
    return (
      <React.Fragment>
        {searchbar}
        <Redirect to={`/view/${commit.trim()}`}/>
      </React.Fragment>
    )
  }

  return searchbar;
}