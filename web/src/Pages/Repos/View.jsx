import React from "react";
import {Redirect} from "react-router-dom";

import {makeStyles} from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import CircularProgress from "@material-ui/core/CircularProgress";

import ReposTable from "./Table";
import useGet from "../../useGet";

const useStyles = makeStyles({
  root: {
    flexGrow: 1,
  },
  table: {
    minWidth: 500,
  },
  headerText: {
    fontWeight: 600
  },
  commitHashContainer: {
    width: 200,
    overflow: "hidden",
  }
});

export default function Repos() {
  const classes = useStyles();
  const {loading, error, data} = useGet('/api/public/repos');

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  return (
    <Grid
      container
      direction="column"
      justify="center"
      alignItems="center"
    >
      <Grid item xs={12}>
        <ReposTable rows={data.repos}/>
      </Grid>
    </Grid>
  );
}