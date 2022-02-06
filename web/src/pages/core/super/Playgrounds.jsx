import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@material-ui/data-grid';
import green from '@material-ui/core/colors/green';
import Grid from '@material-ui/core/Grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import Fab from '@material-ui/core/Fab';
import RefreshIcon from '@material-ui/icons/Refresh';
import Tooltip from '@material-ui/core/Tooltip';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';


const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
  dataGrid: {
    height: '100%',
  },
  button: {
    marginRight: theme.spacing(1),
  },
}));

const stopSession = (id, state, enqueueSnackbar) => () => {
  const {setReset} = state;
  axios.get(`/api/super/playgrounds/stop/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const stopAllSessions = (state, enqueueSnackbar) => () => {
  const {setReset} = state;
  axios.get(`/api/super/playgrounds/reap-all`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const useColumns = (state, enqueueSnackbar) => ([
  {field: 'netid', headerName: 'Netid'},
  {field: 'state', headerName: 'State', width: 150},
  {field: 'image', headerName: 'Image', width: 150, valueGetter: (params) => params.value.title},
  {field: 'image_tag', headerName: 'Tag', width: 150, valueGetter: (params) => params.value?.title ?? 'latest'},
  {field: 'created', headerName: 'Created', type: 'dateTime', width: 170},
  {
    field: 'redirect_url', headerName: 'Go To IDE', width: 120, renderCell: ({row}) => (
      <React.Fragment>
        {row.state === 'Running' && (
          <Button
            style={{
              buttonSuccess: {
                'backgroundColor': green[500],
                '&:hover': {
                  backgroundColor: green[700],
                },
              },
            }}
            variant={'contained'}
            color={'primary'}
            component={'a'}
            href={row.redirect_url}
            target={'_blank'}
          >
            Go To IDE
          </Button>
        )}
      </React.Fragment>
    ),
  },
  {
    field: 'kill', headerName: 'Kill Session', width: 150, renderCell: ({row}) => (
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

export default function Playgrounds() {
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
    axios.get('/api/super/playgrounds/list').then((response) => {
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
          Playgrounds Management
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
                disableColumnMenu={true}
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

