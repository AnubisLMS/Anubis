import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/material/styles/makeStyles';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Delete from '@mui/icons-material/Delete';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

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
