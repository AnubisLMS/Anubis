import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import {useHistory} from 'react-router-dom';
import axios from 'axios';

import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';

import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';
import VisibilityIcon from '@material-ui/icons/Visibility';

import green from '@material-ui/core/colors/green';
import grey from '@material-ui/core/colors/grey';

import standardStatusHandler from '../../../../utils/standardStatusHandler';
import ManagementIDEDialog from '../../../../components/core/AdminIDE/ManagementIDEDialog';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));

export default function Assignments() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [reset, setReset] = useState(0);
  const [assignments, setAssignments] = useState([]);
  const history = useHistory();

  React.useEffect(() => {
    axios.get('/api/admin/assignments/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignments) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const addAssignment = () => {
    axios.post('/api/admin/assignments/add').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.assignment) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

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
        <Button variant={'contained'} color={'primary'} onClick={addAssignment}>
          Add Assignment
        </Button>
      </Grid>
      <Grid item xs={12}>
        <ManagementIDEDialog/>
      </Grid>
      <Grid item xs={8}>
        <Paper className={classes.paper}>
          <DataGrid columns={[
            {field: 'name', headerName: 'Assignment Name', width: 200},
            {field: 'hidden', headerName: 'Visibility', width: 110, renderCell: ({row}) => (
              <Tooltip title={
                !row.hidden ? 'Visible to students' : 'Hidden to students'
              }>
                {
                  !row.hidden ?
                    <VisibilityIcon style={{color: green[500]}}/> :
                    <VisibilityOffIcon style={{color: grey[500]}}/>
                }
              </Tooltip>
            )},
            {field: 'release_date', headerName: 'Release Date', width: 170},
            {field: 'due_date', headerName: 'Due Date', width: 170},
          ]} rows={assignments} onRowClick={({row}) => history.push(`/admin/assignment/edit/${row.id}`)}/>
        </Paper>
      </Grid>
    </Grid>
  );
}
