import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import {useSnackbar} from 'notistack';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import axios from 'axios';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import IDEHeader from './IDEHeader';
import IDEInstructions from './IDEInstructions';
import CircularProgress from '@material-ui/core/CircularProgress';
import {green} from '@material-ui/core/colors';
import clsx from 'clsx';

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


const pollSession = (id, state, enqueueSnackbar) => () => {
  const {setLoading, setSession} = state;

  axios.get(`/api/public/ide/poll/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (!data.loading) {
      setSession(data.session);
      setLoading(false);
      return;
    }

    setTimeout(pollSession(id, state, enqueueSnackbar), 1000);
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const startSession = (state, enqueueSnackbar) => () => {
  const {session, setSession, selectedTheia, setLoading} = state;
  if (session) {
    const a = document.createElement('a');
    a.setAttribute('href', session.redirect_url);
    a.setAttribute('target', '_blank');
    a.setAttribute('hidden', true);
    document.body.append(a);
    a.click();
    return;
  }
  setLoading(true);
  axios.get(`/api/public/ide/initialize/${selectedTheia.id}`).then((response) => {
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
  const {session, setSession, setLoading} = state;
  if (!session) {
    return;
  }
  setLoading(true);
  axios.get(`/api/public/ide/stop/${session.id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setSession(null);
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

  React.useEffect(() => {
    axios.get('/api/public/ide/available').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setSessionsAvailable(data.sessions_available);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    if (!selectedTheia) {
      return null;
    }

    axios.get(`/api/public/ide/active/${selectedTheia.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setSession(data.session);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedTheia]);

  const state = {
    selectedTheia, setSelectedTheia,
    sessionsAvailable, setSessionsAvailable,
    loading, setLoading,
    session, setSession,
  };

  return (
    <Dialog
      open={selectedTheia !== null}
      onClose={() => setSelectedTheia(null)}
    >
      <DialogTitle>Anubis Cloud IDE</DialogTitle>
      <DialogContent>
        <IDEHeader sessionsAvailable={sessionsAvailable}/>
        <DialogContentText>
          By using the Anubis Cloud IDE, you are agreeing to a few things. Please read the
          full instructions before use.
        </DialogContentText>
        <IDEInstructions/>
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
            disabled={loading}
            onClick={startSession(state, enqueueSnackbar)}
            variant={'contained'}
            color={'primary'}
            autoFocus
          >
            {!session ? 'Launch Session' : 'Go to IDE'}
          </Button>
          {loading && <CircularProgress size={24} className={classes.buttonProgress} />}
        </div>
      </DialogActions>
    </Dialog>
  );
}
