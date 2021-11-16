import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@material-ui/data-grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Delete from '@material-ui/icons/Delete';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
}));

export default function AssignmentReposTable({repos, setReset}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const deleteRepo = (id) => () => {
    axios.delete(`/api/admin/assignments/repo/${id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

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
        {field: 'delete', headerName: 'Delete', width: 150, renderCell: ({row}) => (
          <Button color={'secondary'} variant={'contained'} startIcon={<Delete/>} onClick={deleteRepo(row.id)}>
            repo
          </Button>
        )},
      ]} rows={repos}/>
    </Paper>
  );
}
