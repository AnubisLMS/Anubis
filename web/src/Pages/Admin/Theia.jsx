import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import Fab from '@material-ui/core/Fab';
import RefreshIcon from '@material-ui/icons/Refresh';
import Tooltip from '@material-ui/core/Tooltip';


const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    padding: theme.spacing(1),
  },
  dataGrid: {
    height: '100%',
  },
  button: {
    margin: theme.spacing(1),
  },
}));

const stopSession = (id, state, enqueueSnackbar) => () => {
  const {setReset} = state;
  axios.get(`/api/admin/ide/stop/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const stopAllSessions = (state, enqueueSnackbar) => () => {
  const {setReset} = state;
  axios.get(`/api/admin/ide/reap-all`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const useColumns = (state, enqueueSnackbar) => ([
  {field: 'netid', headerName: 'Netid'},
  {field: 'state', headerName: 'State'},
  {field: 'course_code', headerName: 'Course', width: 150},
  {field: 'created', headerName: 'Created', type: 'dateTime', width: 200},
  {
    field: 'kill', headerName: 'End Session', width: 150, renderCell: ({row}) => (
      <Button
        variant={'contained'}
        color={'secondary'}
        size={'small'}
        startIcon={<DeleteForeverIcon/>}
        onClick={stopSession(row.id, state, enqueueSnackbar)}
      >
        Kill Session
      </Button>
    ),
  },
]);

export default function Theia() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [sessions, setSessions] = useState([]);
  const [rows, setRows] = useState([]);
  const [edits, setEdits] = useState(0);
  const [reset, setReset] = useState(0);

  const state = {
    sessions, setSessions,
    rows, setRows,
    edits, setEdits,
    reset, setReset,
  };

  const columns = useColumns(state, enqueueSnackbar);


  React.useEffect(() => {
    axios.get('/api/admin/ide/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);

      if (data) {
        setSessions([...data.sessions]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  React.useEffect(() => {
    setRows(sessions);
  }, [sessions]);

  return (
    <Grid container spacing={4} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Course Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <Button
          variant={'contained'}
          color={'secondary'}
          className={classes.button}
          onClick={stopAllSessions(state, enqueueSnackbar)}
        >
          Kill All Sessions
        </Button>
        <Tooltip title={'Reload session data'}>
          <Fab
            size={'small'}
            className={classes.button}
            color={'primary'}
            onClick={() => setReset((prev) => ++prev)}
          >
            <RefreshIcon/>
          </Fab>
        </Tooltip>
      </Grid>
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <DataGrid
                className={classes.dataGrid}
                columns={columns}
                rows={rows}
              />
            </Paper>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
