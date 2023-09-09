import React, {useEffect, useState} from 'react';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';

// import AprilFools from '../../../../components/core/AprilFools/2023/AprilFools';
// import MaintenanceAd from '../../../../components/shared/Ad/MaintenanceAd/MaintenanceAd';
import DiscordBanner from '../../../../components/core/DiscordBanner/DiscordBanner';
import GenericAd from '../../../../components/shared/Ad/GenericAd/GenericAd';
import ListHeader from '../../../../components/shared/ListHeader/ListHeader';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import {useStyles} from './Playgrounds.styles';
import {ideStartDelay} from '../../../../constant';

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
        }, ideStartDelay);
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

// TODO -- remove once pincer study is over
const disabledImages = [
  '41978cdaa08b915c5708030e8f81f1b3',
  'ae6ae9cdddfcb1577ec2fdd8aa3e046c',
];

export default function Playgrounds({imageId}) {
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
      if (imageId) {
        const focusedImages = data.images.filter((image) => image.id === imageId);
        setAvailableImages(focusedImages);
        setSelectedImage(focusedImages[0]);
      } else {
        // TODO -- remove once pincer study is over.
        setAvailableImages(data.images.filter((s) => !disabledImages.includes(s.id)));
        setSelectedImage(data?.images[0]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (!availableImages) return undefined;
    axios.get(`/api/public/playgrounds/active`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.session) {
        setShowStop(true);
        setSessionState(data.session.state);
        setSession(data.session);
        setSelectedTag(data.session.image_tag);
        setSelectedImage(data.session.image);
        if (data.session?.state === 'Initializing') {
          setLoading(true);
          pollSession(data.session.id, state, enqueueSnackbar)();
        }
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [availableImages]);

  useEffect(() => {
    if (!selectedImage) return undefined;
    const defaultTags = [{title: 'latest', description: null}];
    let tags = selectedImage?.tags ?? defaultTags;
    if (tags.length === 0) {
      tags = defaultTags;
    }
    setAvailableTags(tags);
    if (selectedTag?.image_id !== selectedImage.id) {
      setSelectedTag(tags[0]);
    }
  }, [selectedImage]);

  const Image = ({title, icon, isSelected}) => {
    return (
      <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
        <Box className={classes.imageHeader}>
          <i
            className={clsx(icon, isSelected ?
              clsx(classes.icon, classes.opFull) :
              clsx(classes.icon, classes.opLess))}
            style={{fontSize: 32}}/>
          <Typography className={isSelected ? classes.opFull : classes.opLess}>{title}</Typography>
        </Box>
      </Box>
    );
  };

  const Tag = ({title, isSelected}) => (
    <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
      <Box className={classes.imageHeader}>
        <Typography>{title}</Typography>
      </Box>
    </Box>
  );

  return (
    <StandardLayout>
      <SectionHeader isPage title={'Playgrounds'}/>
      <Box className={classes.divider}/>
      {/* <MaintenanceAd/>*/}
      <GenericAd/>
      <DiscordBanner/>
      {/* <AprilFools/>*/}
      <ListHeader sections={['Your Playground', sessionState || 'No Active IDE']}/>
      <Box className={classes.imageTagContainer}>
        <Grid container xs={12} spacing={2}>
          <Grid item xs={12}>
            <Typography variant={'body1'} gutterBottom>
              With Anubis Playgrounds you can run any of the IDEs we provide with one click. No course sign up
              necessary. Select an IDE, and a version and hit launch to start.
            </Typography>
            <Typography variant={'body2'} component={'small'} style={{color: 'grey'}} gutterBottom>
              {'Don\'t see an IDE you need? Open an issue on our github ' +
                'requesting what you need, and we\'ll see if we can add it!'}
            </Typography>
          </Grid>
          {availableImages && selectedImage && availableImages.map((image, index) => (
            <Grid
              item
              xs={12}
              sm={6}
              md={4}
              lg={3}
              className={classes.imageContainer}
              onClick={() => setSelectedImage(image)} key={index}
            >
              <Tooltip title={image.description}>
                <Box>
                  <Image
                    {...image}
                    isSelected={selectedImage?.id === image.id}
                  />
                </Box>
              </Tooltip>
            </Grid>
          ))}
        </Grid>
        <Box className={classes.divider}/>
        <Grid container className={classes.tagListContainer} md={12} xs={12} spacing={2}>
          {availableTags && selectedTag && availableTags.map((tag, index) => (
            <Grid
              item
              xs={12}
              sm={6}
              md={4}
              lg={3}
              onClick={() => setSelectedTag(tag)}
              key={index}
            >
              <Tooltip title={tag.description}>
                <Box>
                  <Tag
                    {...tag}
                    isSelected={selectedTag?.id === tag.id}
                  />
                </Box>
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
              {!session ? 'Launch Session' : 'Go to IDE'}
              {loading && <CircularProgress size={24} className={classes.buttonProgress}/>}
            </Button>
          </Grid>
          <Grid item xs={12} sm={3} hidden={!showStop}>
            <Button
              onClick={stopSession(state, enqueueSnackbar)}
              variant={'contained'}
              color={'error'}
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
