import React, {useState} from 'react';
import clsx from 'clsx';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import green from '@mui/material/colors/green';
import Dialog from '@mui/material/Dialog';
import makeStyles from '@mui/styles/makeStyles';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import Typography from '@mui/material/Typography';
import CodeOutlinedIcon from '@mui/icons-material/CodeOutlined';
import Autocomplete from '@mui/lab/Autocomplete';

import IDEHeader from '../IDE/IDEHeader';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

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
  axios.post(`/api/admin/ide/initialize`, {settings}).then((response) => {
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
  const [images, setImages] = useState([]);
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
    axios.get(`/api/admin/ide/images/list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.images) {
        setImages(data.images);
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
      return undefined;
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
      } else {
        prev[key] = e;
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
              <Autocomplete
                fullWidth
                disableClearable
                value={settings.image}
                onChange={(_, v) => updateSetting('image')(v)}
                options={images}
                getOptionLabel={(option) => option?.title}
                renderInput={(params) => <TextField {...params} label="IDE Image" variant="outlined" />}
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
                label="admin"
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
