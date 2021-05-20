import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';
import VisibilityIcon from '@material-ui/icons/Visibility';
import green from '@material-ui/core/colors/green';
import grey from '@material-ui/core/colors/grey';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import ManagementIDEDialog from '../../../Components/Admin/IDE/ManagementIDEDialog';
import {Tooltip} from '@material-ui/core';
import {Redirect} from 'react-router-dom';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));

export default function Assignments() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [redirect, setRedirect] = useState(null);

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignments) {
        setAssignments(data.assignments);
      }
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, []);

  if (redirect !== null) {
    return <Redirect to={redirect}/>;
  }


  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignment Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <ManagementIDEDialog/>
      </Grid>
      <Grid item xs={8}>
        <Paper className={classes.paper}>
          <DataGrid columns={[
            {field: 'name', headerName: 'Assignment Name', width: 200},
            {field: 'hidden', headerName: 'Hidden', width: 100, renderCell: ({row}) => (
              <Tooltip title={row.hidden ? 'Hidden' : 'Visible'}>
                {
                  row.hidden ?
                    <VisibilityOffIcon style={{color: grey[500]}}/> :
                    <VisibilityIcon style={{color: green[500]}}/>
                }
              </Tooltip>
            )},
            {field: 'release_date', headerName: 'Release Date', width: 170},
            {field: 'due_date', headerName: 'Due Date', width: 170},
          ]} rows={assignments} onRowClick={({row}) => setRedirect(`/admin/assignment/edit/${row.id}`)}/>
        </Paper>
      </Grid>
    </Grid>
  );
}
