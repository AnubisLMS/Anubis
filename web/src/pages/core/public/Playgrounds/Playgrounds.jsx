import React, {useEffect, useState} from 'react';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import InfoIcon from '@material-ui/icons/Info';

import ListHeader from '../../../../components/shared/ListHeader/ListHeader';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import {useStyles} from './Playgrounds.styles';

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
          <i
            className={clsx(icon, isSelected ? clsx(classes.icon, classes.opFull) : clsx(classes.icon, classes.opLess))}
            style={{fontSize: 24}}/>
          <Typography className={isSelected ? classes.opFull : classes.opLess}>{title}</Typography>
        </Box>
        <br/>
        <Tooltip
          title={description}
          className={classes.tooltip}
        >
          <InfoIcon className={isSelected ? classes.opFull : classes.opLess}/>
        </Tooltip>
      </Box>
    );
  };

  const Tag = ({title, description, isSelected}) => (
    <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
      <Box className={classes.imageHeader}>
        <Typography>{title}</Typography>
      </Box>
      <br/>
      <Typography variant={'body1'}>
        {description}
      </Typography>
    </Box>
  );

  return (
    <StandardLayout>
      <SectionHeader isPage title={'Playgrounds'}/>
      <Box className={classes.divider}/>
      <ListHeader sections={['Your Playground', sessionState || 'No Active AdminIDE']}/>
      <Box className={classes.imageTagContainer}>
        <Grid container md={12} xs={12} spacing={2}>
          {availableImages && selectedImage && availableImages.map((image, index) => (
            <Grid
              item
              xs={12}
              sm={6}
              md={3}
              className={classes.imageContainer}
              onClick={() => setSelectedImage(image)} key={index}
            >
              <Tooltip title={image.description}>
                <Image
                  {...image}
                  isSelected={selectedImage?.id === image.id}
                />
              </Tooltip>
            </Grid>
          ))}
        </Grid>
        <Box className={classes.divider}/>
        <Grid container className={classes.tagListContainer} md={12} xs={12} spacing={2}>
          {availableTags && selectedTag && availableTags.map((tag, index) => (
            <Grid item xs={12} sm={6} md={3} onClick={() => setSelectedTag(tag)} key={index}>
              <Tooltip title={tag.description}>
                <Tag
                  {...tag}
                  isSelected={selectedTag?.id === tag.id}
                />
              </Tooltip>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Box className={classes.actionContainer}>
        <Grid container md={12} xs={12} spacing={2}>
          <Grid item xs={12} sm={3}>
            <Button
              className={clsx(classes.button, {
                [classes.buttonSuccess]: session,
              })}
              disabled={loading || !sessionsAvailable}
              onClick={startSession(state, enqueueSnackbar)}
              variant={'contained'}
              color={'primary'}
              autoFocus
            >
              {!session ? 'Launch Session' : 'Go to AdminIDE'}
              {loading && <CircularProgress size={24} className={classes.buttonProgress}/>}
            </Button>
          </Grid>
          <Grid item xs={12} sm={3} hidden={!showStop}>
            <Button
              onClick={stopSession(state, enqueueSnackbar)}
              variant={'contained'}
              color={'secondary'}
              autoFocus
              className={classes.button}
            >
              Stop Session
            </Button>
          </Grid>
        </Grid>
      </Box>
    </StandardLayout>
  );
}
