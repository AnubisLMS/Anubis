import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
}));

export default function AssignmentReposTable({repos}) {
  const classes = useStyles();

  return (
    <Paper className={classes.paper}>
      <DataGrid columns={[
        {field: 'netid', headerName: 'netid', width: 100},
        {field: 'name', headerName: 'Name', width: 200},
        {field: 'github_username', headerName: 'Github Username', width: 200},
        {field: 'url', headerName: 'Repo URL', width: 150, renderCell: (params) => (
          <Typography href={params.row.url} target="_blank" rel="noreferrer" component={'a'}>
            repo
          </Typography>
        )},
      ]} rows={repos}/>
    </Paper>
  );
}
