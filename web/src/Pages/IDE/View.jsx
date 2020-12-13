import React from "react";
import {makeStyles} from "@material-ui/core/styles";
import CircularProgress from "@material-ui/core/CircularProgress";
import {Redirect} from "react-router-dom";
import useSubscribe from "../../useSubscribe";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import IDETable from "./Table";
import Warning from "./Warning";


const useStyles = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
  instructions: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  }
}));


export default function IDE() {
  const classes = useStyles();
  const {loading, error, data} = useSubscribe(
    '/api/public/ide/list',
    1000,
    _data => new Array(..._data.sessions).every(item => (
      item.state !== 'Initializing' && item.state !== 'Ending'
    )),
  );

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  return (
    <div className={classes.root}>
      <Grid container
            direction="row"
            justify="center"
            alignItems="center"
            spacing={6}>

        <Grid item xs={12}>
          <Typography variant="h6" className={classes.subtitle}>
            Anubis Cloud IDE
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Warning/>
        </Grid>

        <Grid item xs={12}>
          <IDETable
            headers={[
              "Session State",
              "Session Active",
              "End Session",
              "Launch Session",
              "Assignment Name",
              "Class Name",
              "Assignment Repo",
              "Created",
            ]}
            rows={new Array(...data.sessions)}
          />
        </Grid>
      </Grid>
    </div>
  );
}