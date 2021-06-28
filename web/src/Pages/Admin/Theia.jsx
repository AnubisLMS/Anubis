import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Grid from '@material-ui/core/Grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import Fab from '@material-ui/core/Fab';
import RefreshIcon from '@material-ui/icons/Refresh';
import Tooltip from '@material-ui/core/Tooltip';
import GitHubIcon from '@material-ui/icons/GitHub';
import IconButton from '@material-ui/core/IconButton';
import CheckIcon from '@material-ui/icons/Check';
import CancelIcon from '@material-ui/icons/Cancel';

import {CustomGrid} from '../../Components/Shared';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import ManagementIDEDialog from '../../Components/Admin/IDE/ManagementIDEDialog';


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
  {field: 'state', headerName: 'State'},
  {field: 'course_code', headerName: 'Course', width: 120},
  {field: 'assignment_name', headerName: 'Assignment', width: 200},
  {field: 'created', headerName: 'Created', type: 'dateTime', width: 170},
  {field: 'autosave', headerName: 'Autosave', width: 100, renderCell: ({row}) => (
    <IconButton color={row.autosave ? 'primary' : 'secondary'}>
      {row.autosave ? <CheckIcon/> : <CancelIcon/>}
    </IconButton>
  )},
  {
    field: 'repo_url', headerName: 'Repo', width: 75, renderCell: ({row}) => (
      <IconButton color={'primary'} component={'a'} href={row.repo_url} target={'_blank'}>
        <GitHubIcon/>
      </IconButton>
    ),
  },
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
          Cloud IDE Management
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <ManagementIDEDialog/>
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
      <Grid item xs={12} md={12} lg={10}>
        <CustomGrid {
          ... {
            columns: columns,
            rows: rows,
            disableColumnMenu: true,
          }
        }
        />
      </Grid>
    </Grid>
  );
}
