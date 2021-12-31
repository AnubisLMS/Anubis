import React, {useEffect, useState} from 'react';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';
import {makeStyles} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import green from '@material-ui/core/colors/green';
import Card from '@material-ui/core/Card';
import DialogActions from '@material-ui/core/DialogActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import InfoIcon from '@material-ui/icons/Info';

import StandardLayout from '../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import Divider from '@material-ui/core/Divider';

const useStyles = makeStyles((theme) => ({
  container: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
  paper: {
    width: '100%',
    maxWidth: '700px',
    padding: theme.spacing(2),
  },
  image: {
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'space-between',
    'paddingRight': theme.spacing(2),
    'paddingLeft': theme.spacing(2),
    'marginTop': theme.spacing(1),
    'marginBottom': theme.spacing(1),
    'border': '2px solid gray',
    'borderRadius': '5px',
    'cursor': 'pointer',
    '&:hover': {
      border: `2px solid ${theme.palette.primary.main}`,
    },
  },
  selectedImage: {
    border: `2px solid ${theme.palette.primary.main}`,
  },
  imageHeader: {
    display: 'flex',
    alignItems: 'center',
  },
  imageLabel: {
    marginLeft: theme.spacing(1),
    paddingBottom: theme.spacing(.5),
    paddingTop: theme.spacing(.5),
    paddingRight: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    backgroundColor: theme.palette.primary.main,
    borderRadius: '20px',
  },
  imageDescription: {
    marginTop: -theme.spacing(1),
  },
  button: {
    marginTop: theme.spacing(2),
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
    marginLeft: 'auto',
  },
  buttonWrapper: {
    display: 'flex',
    flexDirection: 'row',
  },
  icon: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
  },
  tooltip: {
    fontSize: '16px',
  },
}));

const stopSession = (state, enqueueSnackbar) => () => {
  const {session, setSession, setLoading, setSessionState, setShowStop} = state;
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
    }
    setLoading(false);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

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
  const {setSession, session, selectedImage, selectedTag, setLoading, setShowStop} = state;
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
  axios.post(`/api/public/playgrounds/initialize/${selectedImage.id}`, null, {
    params: {tag: selectedTag?.id ?? 'latest'},
  }).then((response) => {
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

export default function Playgrounds() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [sessionsAvailable, setSessionsAvailable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(false);
  const [sessionState, setSessionState] = useState(null);
  const [showStop, setShowStop] = useState(false);
  const [availableImages, setAvailableImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [availableTags, setAvailableTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState(null);

  const state = {
    selectedImage, setSelectedImage,
    sessionsAvailable, setSessionsAvailable,
    availableTags, setAvailableTags,
    selectedTag, setSelectedTag,
    loading, setLoading,
    session, setSession,
    sessionState, setSessionState,
    showStop, setShowStop,
  };

  useEffect(() => {
    axios.get('/api/public/ide/available').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session_available) {
        setSessionsAvailable(data.session_available);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    axios.get(`/api/public/playgrounds/images`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setAvailableImages(data.images);
      setSelectedImage(data?.images[0]);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (!selectedImage) return null;
    axios.get(`/api/public/playgrounds/active`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session) {
        setSessionState(data.session.state);
        setSession(data.session);
      }
      if (data?.session?.state === 'Initializing') {
        setLoading(true);
        pollSession(data.session.id, state, enqueueSnackbar)();
      }
      if (data?.session?.state === 'Running') {
        setShowStop(true);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
    const defaultTags = [{title: 'latest', description: null}];
    let tags = selectedImage?.tags ?? defaultTags;
    if (tags.length === 0) {
      tags = defaultTags;
    }
    setAvailableTags(tags);
    setSelectedTag(tags[0]);
  }, [selectedImage]);

  const Image = ({title, description, icon, isSelected}) => {
    return (
      <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
        <Box className={classes.imageHeader}>
          <i className={clsx(icon, classes.icon)} style={{fontSize: 24}}/>
          <h3>{title}</h3>
        </Box>
        <br/>
        <Tooltip
          title={description}
          className={classes.tooltip}
        >
          <InfoIcon />
        </Tooltip>
      </Box>
    );
  };

  const Tag = ({title, description, isSelected}) => (
    <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
      <Box className={classes.imageHeader}>
        <h3>{title}</h3>
      </Box>
      <br/>
      <Typography variant={'body1'}>
        {description}
      </Typography>
    </Box>
  );

  return (
    <StandardLayout
      title={'Anubis'}
      description={'Playground'}
    >
      <Box className={classes.container}>
        <Card className={classes.paper}>
          <CardHeader
            title={'Anubis Playgrounds'}
          />
          <CardContent>
            <Grid container md={12} xs={12} spacing={2}>
              <Grid item xs={12}>
                <Typography>
                  Please select one of the below images to launch your session
                </Typography>
              </Grid>
              <React.Fragment>
                {availableImages && selectedImage && availableImages.map((image, index) => (
                  <Grid item xs={12} sm={6} onClick={() => setSelectedImage(image)} key={index}>
                    <Tooltip title={image.description}>
                      <Image
                        {...image}
                        isSelected={selectedImage?.id === image.id}
                      />
                    </Tooltip>
                  </Grid>
                ))}
              </React.Fragment>
              <Grid item xs={12}>
                <Divider variant={'middle'} style={{height: 2, backgroundColor: 'white'}}/>
              </Grid>
              <React.Fragment>
                {availableTags && selectedTag && availableTags.map((tag, index) => (
                  <Grid item xs={12} sm={6} onClick={() => setSelectedTag(tag)} key={index}>
                    <Tooltip title={tag.description}>
                      <Tag
                        {...tag}
                        isSelected={selectedTag?.id === tag.id}
                      />
                    </Tooltip>
                  </Grid>
                ))}
              </React.Fragment>
              <Grid item xs={12}>
                <div style={{display: 'flex', justifyContent: 'flex-end'}}>
                  <Typography>
                    {sessionState || 'No Active IDE'}
                  </Typography>
                </div>
              </Grid>
            </Grid>
          </CardContent>
          <DialogActions>
            <div className={clsx(classes.wrapper, classes.left)} hidden={!showStop}>
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
        </Card>
      </Box>

    </StandardLayout>
  );
}
