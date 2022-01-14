import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import green from '@material-ui/core/colors/green';
import Grid from '@material-ui/core/Grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutlineOutlinedIcon from '@material-ui/icons/HelpOutlineOutlined';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import IDEInstructions from './IDEInstructions';
import IDEHeader from './IDEHeader';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  buttonProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  wrapper: {
    position: 'relative',
  },
  buttonSuccess: {
    'backgroundColor': green[500],
    '&:hover': {
      backgroundColor: green[700],
    },
  },
  left: {
    float: 'left',
  },
}));

const checkSession = (id, state, enqueueSnackbar, after = null) => {
  if (id === undefined || id === null) {
    if (after !== null) {
      after();
    }
    return;
  }

  const {setLoading, setSession, setSessionState, setShowStop} = state;

  axios.get(`/api/public/ide/poll/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);

    setSessionState(data.session?.state ?? '');
    if (!data.loading) {
      if (data.session.state === 'Running') {
        setTimeout(() => {
          setSession(data.session);
          setLoading(false);
          setShowStop(true);
        }, 1000);
      } else {
        setSession(null);
        setLoading(false);
        setShowStop(false);
      }
      return;
    }

    if (after !== null) {
      after();
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const pollSession = (id, state, enqueueSnackbar, n = 0) => () => {
  const {setShowStop} = state;

  if (n === 30) {
    setShowStop(true);
  }

  if (n > 600) {
    return;
  }

  checkSession(
    id,
    state,
    enqueueSnackbar,
    () => setTimeout(pollSession(id, state, enqueueSnackbar, ++n), 1000),
  );
};

const startSession = (state, enqueueSnackbar) => () => {
  const {autosaveEnabled, persistentStorage, setSession, session, selectedTheia, setLoading, setShowStop} = state;
  if (session) {
    const a = document.createElement('a');
    a.setAttribute('href', session.redirect_url);
    a.setAttribute('target', '_blank');
    a.setAttribute('hidden', true);
    document.body.append(a);
    a.click();
    return;
  }

  const params = {autosave: autosaveEnabled, persistent_storage: persistentStorage};
  setLoading(true);
  axios.post(`/api/public/ide/initialize/${selectedTheia.id}`, {params}).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data?.session) {
      setShowStop(false);
      setSession(data.session);
      pollSession(data.session.id, state, enqueueSnackbar)();
    } else {
      setLoading(false);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const stopSession = (state, enqueueSnackbar) => () => {
  const {session, setAutosaveEnabled, setSession, setLoading, setSessionState, setShowStop} = state;
  if (!session) {
    return;
  }
  setShowStop(false);
  setLoading(true);
  axios.get(`/api/public/ide/stop/${session.id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setSessionState('Stopped');
      setSession(null);
      setAutosaveEnabled(true);
    }
    setLoading(false);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function IDEDialog({selectedTheia, setSelectedTheia}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [sessionsAvailable, setSessionsAvailable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(false);
  const [sessionState, setSessionState] = useState(null);
  const [autosaveEnabled, setAutosaveEnabled] = useState(true);
  const [persistentStorage, setPersistentStorage] = useState(false);
  const [showPersistentStorage, setShowPersistentStorage] = useState(false);
  const [showAutosave, setShowAutosave] = useState(false);
  const [assignment, setAssignment] = useState(null);
  const [showStop, setShowStop] = useState(false);

  React.useEffect(() => {
    axios.get('/api/public/ide/available').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session_available) {
        setSessionsAvailable(data.session_available);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    if (!selectedTheia) {
      return null;
    }

    axios.get(`/api/public/assignments/get/${selectedTheia.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.assignment) {
        setAssignment(data.assignment);
        if (data.assignment?.persistent_storage !== undefined) {
          setShowPersistentStorage(!!data.assignment.persistent_storage);
          setPersistentStorage(data.assignment.persistent_storage);

          setShowAutosave(!!data.assignment.autosave);
          setAutosaveEnabled(!!data.assignment.autosave);
        }
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedTheia]);

  React.useEffect(() => {
    if (!selectedTheia) {
      return null;
    }

    axios.get(`/api/public/ide/active/${selectedTheia.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session) {
        setSessionState(data.session.state);
        setSession(data.session);
      }
      if (data?.session?.autosave !== undefined) {
        setAutosaveEnabled(data.session.autosave);
      }
      if (data?.session?.persistent_storage !== undefined) {
        setPersistentStorage(data.session.persistent_storage);
      }
      if (data?.session?.state === 'Initializing') {
        setLoading(true);
        pollSession(data.session.id, state, enqueueSnackbar)();
      }
      if (data?.session?.state === 'Running') {
        setShowStop(true);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedTheia]);

  const state = {
    selectedTheia, setSelectedTheia,
    sessionsAvailable, setSessionsAvailable,
    loading, setLoading,
    session, setSession,
    autosaveEnabled, setAutosaveEnabled,
    persistentStorage, setPersistentStorage,
    assignment, setAssignment,
    sessionState, setSessionState,
    showPersistentStorage, setShowPersistentStorage,
    showAutosave, setShowAutosave,
    showStop, setShowStop,
  };

  return (
    <Dialog
      open={selectedTheia !== null}
      onClose={() => setSelectedTheia(null)}
      onFocus={() => session && checkSession(session.id, state, () => null)}
    >
      <DialogTitle>Anubis Cloud IDE</DialogTitle>
      <DialogContent>
        <Grid
          container
          direction="row"
          justify="flex-end"
          alignItems="center"
        >
          <Grid item xs={12}>
            <IDEHeader sessionsAvailable={sessionsAvailable}/>
          </Grid>
          <Grid item xs={12}>
            <DialogContentText>
              By using the Anubis Cloud IDE, you are agreeing to a few things. Please read the
              full instructions before use.
            </DialogContentText>
          </Grid>
          <Grid item xs={12}>
            <IDEInstructions/>
          </Grid>
          {showAutosave && (
            <Grid item xs={12}>
              <FormControlLabel
                disabled={!!session}
                checked={autosaveEnabled}
                onChange={() => setAutosaveEnabled(!autosaveEnabled)}
                control={<Switch color={'primary'}/>}
                label={
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <Typography color={autosaveEnabled ? '' : 'secondary'} variant={'body1'}>
                      {autosaveEnabled ?
                        'Autosave Enabled' :
                        (
                          'With autosave disabled you are responsible for saving your progress. ' +
                          'No exceptions will be made for lost work!'
                        )}
                    </Typography>
                    <Tooltip title={persistentStorage ?
                      'Anubis will automatically try to commit and push any git repo in /home/anubis to github ' +
                      'every 5 minutes. You can also use the autosave command in the terminal ' +
                      'to manually tell Anubis ' +
                      'to commit and push. It is still your ' +
                      'responsibility to make sure that your work is saved, and submitted on time.' :
                      'Anubis will not try to automatically commit and push your work to github. It is your ' +
                      'responsibility to make sure that your work is saved, and submitted on time.'}>
                      <IconButton>
                        <HelpOutlineOutlinedIcon fontSize={'small'}/>
                      </IconButton>
                    </Tooltip>
                  </div>
                }
                labelPlacement="end"
              />
            </Grid>
          )}
          {showPersistentStorage && (
            <Grid item xs={12}>
              <FormControlLabel
                disabled={!!session}
                checked={persistentStorage}
                onChange={() => setPersistentStorage(!persistentStorage)}
                control={<Switch color={'primary'}/>}
                label={
                  <div style={{display: 'flex', alignItems: 'center'}}>
                    <Typography variant={'body1'}>
                      Persistent Storage
                    </Typography>
                    <Tooltip title={persistentStorage ?
                      'Anubis will mount a persistent volume to your session. Everything in /home/anubis ' +
                      'will be saved in your Cloud AdminIDE volume. We recommend still making sure valuble data is backed' +
                      'up elsewhere.' :
                      'Anubis will not mount a persistent volume to your session. All work not saved elsewhere (like ' +
                      'github) will be deleted when the session ends.'}>
                      <IconButton>
                        <HelpOutlineOutlinedIcon fontSize={'small'}/>
                      </IconButton>
                    </Tooltip>
                  </div>
                }
                labelPlacement="end"
              />
            </Grid>
          )}
          <Grid item xs={12}>
            <div style={{display: 'flex', justifyContent: 'flex-end'}}>
              <Typography>
                {sessionState || 'No Active AdminIDE'}
              </Typography>
            </div>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <div className={classes.wrapper} hidden={!showStop}>
          <Button
            onClick={stopSession(state, enqueueSnackbar)}
            variant={'contained'}
            color={'secondary'}
            autoFocus
          >
            Stop Session
          </Button>
        </div>

        <div className={classes.wrapper}>
          <Button
            className={clsx({
              [classes.buttonSuccess]: session,
            })}
            disabled={loading || !sessionsAvailable}
            onClick={startSession(state, enqueueSnackbar)}
            variant={'contained'}
            color={'primary'}
            autoFocus
          >
            {!session ? 'Launch Session' : 'Go to AdminIDE'}
          </Button>
          {loading && <CircularProgress size={24} className={classes.buttonProgress}/>}
        </div>
      </DialogActions>
    </Dialog>
  );
}
