import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import green from '@material-ui/core/colors/green';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';

import IDEHeader from '../../Public/IDE/IDEHeader';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';

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
  disclaimer: {
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
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
  const {session, settings, setSession, setLoading, setSettings} = state;
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
  axios.post(`/api/admin/ide/initialize-custom`, {settings}).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data.settings) {
      setSettings(data.settings);
    }
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
  axios.get(`/api/admin/ide/stop/${session.id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      setSession(null);
    }
    setLoading(false);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function ManagementIDEDialog() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [open, setOpen] = useState(false);
  const [sessionsAvailable, setSessionsAvailable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(false);
  const [settings, setSettings] = useState({});

  React.useEffect(() => {
    axios.get('/api/public/ide/available').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setSessionsAvailable(data.session_available);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    axios.get('/api/admin/ide/settings').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.settings) {
        setSettings(data.settings);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  React.useEffect(() => {
    if (!open) {
      return null;
    }

    axios.get(`/api/admin/ide/active`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.settings) {
        setSettings(data.settings);
      }
      if (data.session) {
        setTimeout(() => {
          setSession(data.session);
        }, 1000);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [open]);

  const updateSetting = (key) => (e) => {
    setSettings((prev) => {
      if (typeof prev[key] === 'string') {
        prev[key] = e.target.value;
      } else if (typeof prev[key] === 'boolean') {
        prev[key] = !prev[key];
      }
      return {...prev};
    });
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleOpen = () => {
    setOpen(true);
  };

  const state = {
    open, setOpen,
    sessionsAvailable, setSessionsAvailable,
    loading, setLoading,
    session, setSession,
    settings, setSettings,
    handleClose, handleOpen,
  };

  return (
    <div>
      <Button
        variant={'contained'}
        color={'primary'}
        startIcon={<CodeOutlinedIcon/>}
        onClick={handleOpen}
      >
        Management IDE
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
      >
        <DialogTitle>Anubis Cloud IDE</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <IDEHeader sessionsAvailable={sessionsAvailable}/>
            </Grid>
            <Grid item xs={12}>
              <Typography variant={'body2'} className={classes.disclaimer}>
                These are the default settings for the management IDE. Unless you want to
                launch a custom session, you should not change these values.
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth label="Theia Image" variant="outlined"
                value={settings.image} onChange={updateSetting('image')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth label="Repo URL" variant="outlined"
                value={settings.repo_url} onChange={updateSetting('repo_url')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth label="Resources JSON" variant="outlined"
                value={settings.resources} onChange={updateSetting('options')}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth label="Network Policy" variant="outlined"
                value={settings.network_policy} onChange={updateSetting('network_policy')}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.admin} onChange={updateSetting('admin')}
                    name="admin" color="primary"
                  />
                }
                labelPlacement={'end'}
                label="Admin"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.privileged} onChange={updateSetting('privileged')}
                    name="privileged" color="primary"
                  />
                }
                labelPlacement={'end'}
                label="Privileged"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autosave} onChange={updateSetting('autosave')}
                    name="autosave" color="primary"
                  />
                }
                labelPlacement={'end'}
                label="Autosave"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.credentials} onChange={updateSetting('credentials')}
                    name="credentials" color="primary"
                  />
                }
                labelPlacement={'end'}
                label="Credentials"
              />
            </Grid>
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
    </div>
  );
}
