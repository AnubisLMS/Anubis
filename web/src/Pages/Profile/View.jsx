import React, {useState} from "react";
import makeStyles from "@material-ui/core/styles/makeStyles";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import CircularProgress from "@material-ui/core/CircularProgress";
import SaveIcon from '@material-ui/icons/Save';
import {Redirect} from "react-router-dom";
import axios from "axios";
import useGet from "../../useGet";

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
  },
  card: {
    minWidth: 300,
  },
  cardContent: {
    flexDirection: "column",
    display: "flex"
  },
  textField: {
    margin: theme.spacing(1),
  }
}));


export default function Profile() {
  const classes = useStyles();
  const [_github_username, set_github_username] = useState(null);
  const {loading, error, data} = useGet('/api/public/whoami');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  const {user} = data;

  const github_username = _github_username || user.github_username;

  return (
    <Grid
      container
      direction={"column"}
      justify="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <Card variant="outlined" className={classes.card}>
          <CardContent className={classes.cardContent}>
            <Typography className={classes.title} color="textSecondary" gutterBottom>
              Anubis profile
            </Typography>
            <TextField
              disabled
              label="Name"
              className={classes.textField}
              value={user.name.trim()}
              variant="outlined"
            />
            <TextField
              disabled
              label="Netid"
              className={classes.textField}
              value={user.netid.trim()}
              variant="outlined"
            />
            <TextField
              disabled
              label="Github Username"
              className={classes.textField}
              onChange={e => set_github_username(e.target.value)}
              value={github_username}
              variant="outlined"
            />
          </CardContent>
          {/*<CardActions>*/}
          {/*  <Button*/}
          {/*    variant="contained"*/}
          {/*    color="primary"*/}
          {/*    className={classes.button}*/}
          {/*    startIcon={<SaveIcon/>}*/}
          {/*    onClick={() => axios.get(`/api/public/set-github-username?github_username=${github_username}`)}*/}
          {/*  >*/}
          {/*    Save*/}
          {/*  </Button>*/}
          {/*</CardActions>*/}
        </Card>
      </Grid>
    </Grid>
  )
}

