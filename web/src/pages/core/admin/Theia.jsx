import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@mui/x-data-grid';
import green from '@mui/material/colors/green';
import Grid from '@mui/material/Grid';
import makeStyles from '@mui/styles/makeStyles';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import Fab from '@mui/material/Fab';
import RefreshIcon from '@mui/icons-material/Refresh';
import Tooltip from '@mui/material/Tooltip';
import GitHubIcon from '@mui/icons-material/GitHub';
import IconButton from '@mui/material/IconButton';
import CheckIcon from '@mui/icons-material/Check';
import CancelIcon from '@mui/icons-material/Cancel';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import ManagementIDEDialog from '../../../components/core/AdminIDE/ManagementIDEDialog';


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
  {field: 'name', headerName: 'Name', width: 150},
  {field: 'state', headerName: 'State', width: 150},
  {field: 'course_code', headerName: 'Course', width: 120},
  {field: 'assignment_name', headerName: 'Assignment', width: 200},
  {field: 'created', headerName: 'Created', type: 'dateTime', width: 170},
  {
    field: 'autosave', headerName: 'Autosave', width: 100, renderCell: ({row}) => (
      <IconButton color={row.autosave ? 'primary' : 'error'} size="large">
        {row.autosave ? <CheckIcon/> : <CancelIcon/>}
      </IconButton>
    ),
  },
  {
    field: 'repo_url', headerName: 'Repo', width: 75, renderCell: ({row}) => (
      <IconButton
        color={'primary'}
        component={'a'}
        href={row.repo_url}
        target={'_blank'}
        size="large">
        <GitHubIcon/>
      </IconButton>
    ),
  },
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
        color={'error'}
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
    <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Cloud IDE Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <ManagementIDEDialog/>
      </Grid>
      <Grid item xs={12}>
        <Button
          variant={'contained'}
          color={'error'}
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
