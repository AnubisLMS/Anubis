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

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import IDEInstructions from './IDEInstructions';
import IDEHeader from './IDEHeader';
import Typography from '@material-ui/core/Typography';


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


const pollSession = (id, state, enqueueSnackbar, n = 0) => () => {
  const {setLoading, setSession} = state;

  if (n > 60) {
    return;
  }

  axios.get(`/api/public/ide/poll/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (!data.loading) {
      setSession(data.session);
      setLoading(false);
      return;
    }

    setTimeout(pollSession(id, state, enqueueSnackbar, ++n), 1000);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const startSession = (state, enqueueSnackbar) => () => {
  const {autosaveEnabled, session, setSession, selectedTheia, setLoading} = state;
  if (session) {
    const a = document.createElement('a');
    a.setAttribute('href', session.redirect_url);
    a.setAttribute('target', '_blank');
    a.setAttribute('hidden', true);
    document.body.append(a);
    a.click();
    return;
  }

  const params = {autosave: autosaveEnabled};
  setLoading(true);
  axios.get(`/api/public/ide/initialize/${selectedTheia.id}`, {params}).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data.session) {
      if (data.session.state === 'Initializing') {
        pollSession(data.session.id, state, enqueueSnackbar)();
      } else {
        setSession(data.session);
        setLoading(false);
      }
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const stopSession = (state, enqueueSnackbar) => () => {
  const {session, setAutosaveEnabled, setSession, setLoading} = state;
  if (!session) {
    return;
  }
  setLoading(true);
  axios.get(`/api/public/ide/stop/${session.id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
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
  const [autosaveEnabled, setAutosaveEnabled] = useState(true);

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

    axios.get(`/api/public/ide/active/${selectedTheia.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session) {
        setSession(data.session);
      }
      if (data?.session?.autosave !== undefined) {
        setAutosaveEnabled(data.session.autosave);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedTheia]);

  const state = {
    selectedTheia, setSelectedTheia,
    sessionsAvailable, setSessionsAvailable,
    loading, setLoading,
    session, setSession,
    autosaveEnabled, setAutosaveEnabled,
  };

  return (
    <Dialog
      open={selectedTheia !== null}
      onClose={() => setSelectedTheia(null)}
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
          <FormControlLabel
            disabled={!!session}
            checked={autosaveEnabled}
            onChange={() => setAutosaveEnabled(!autosaveEnabled)}
            control={<Switch color={'primary'}/>}
            label={
              <Typography color={autosaveEnabled ? '' : 'secondary'} variant={'body1'}>
                {autosaveEnabled ?
                  'Autosave Enabled' :
                  (
                    'With autosave disabled you are responsible for saving your progress. ' +
                    'No exceptions will be made for lost work!'
                  )}
              </Typography>
            }
            labelPlacement="start"
          />
        </Grid>
      </DialogContent>
      <DialogActions>
        <div className={classes.wrapper} hidden={!session}>
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
            {!session ? 'Launch Session' : 'Go to IDE'}
          </Button>
          {loading && <CircularProgress size={24} className={classes.buttonProgress}/>}
        </div>
      </DialogActions>
    </Dialog>
  );
}
