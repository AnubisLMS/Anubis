import React, {useState, useEffect} from 'react';
import axios from 'axios';
import clsx from 'clsx';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import {makeStyles} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';

import StandardLayout from '../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    width: '100%',
    padding: theme.spacing(2),
  },
  image: {
    paddingTop: theme.spacing(1),
    paddingBottom: theme.spacing(1),
    paddingRight: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    border: '1px solid gray',
    borderRadius: '5px',
    marginTop: theme.spacing(1),
    cursor: 'pointer',
    '&:hover': {
      border: `1px solid ${theme.palette.primary.main}`,
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
}));

export default function Playgrounds() {
  const {enqueueSnackbar} = useSnackbar();
  const [sessionsAvailable, setSessionsAvailable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(false);
  const [sessionState, setSessionState] = useState(null);
  const [showStop, setShowStop] = useState(false);

  const classes = useStyles();

  const [availableImages, setAvailableImages] = useState([
    {
      name: 'python',
      label: '3.0',
      description: 'this is python and it does very cool things',
    },
    {
      name: 'javscript',
      label: 'latest',
      description: 'this is javascript and it does the following things',
    },
  ]);
  const [selectedImage, setSelectedImage] = useState(undefined);
  const [active, setActive] = useState(false);

  const state = {
    selectedImage, setSelectedImage,
    sessionsAvailable, setSessionsAvailable,
    loading, setLoading,
    session, setSession,
    sessionState, setSessionState,
    showStop, setShowStop,
  };

  useEffect(() => {
    axios.get(`/api/public/playgrounds/images`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setAvailableImages(data.images);
      setSelectedImage(data?.images[0]);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (!selectedImage) return null;
    axios.get(`/api/public/ide/active/${selectedImage.id}`).then((response) => {
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
  }, [selectedImage]);

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
    const {setSession, session, selectedImage, setLoading, setShowStop} = state;
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
    axios.post(`/api/public/playgrounds/initialize/${selectedImage.id}`).then((response) => {
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

  const Image = ({name, description, isSelected}) => {
    return (
      <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
        <Box className={classes.imageHeader}>
          <h1>{name}</h1>
        </Box>
        <p className={classes.imageDescription}>{description}</p>
      </Box>
    );
  };

  return (
    <StandardLayout
      title={'Anubis'}
      description={'Playground'}
    >
      <Paper className={classes.paper}>
        <h1>Anubis Playgrounds</h1>
        <p>Please select one of the below images to launch your session</p>
        <Grid container xs={12} spacing={3}>
          {availableImages && selectedImage && availableImages.map((image, index) => (
            <Grid item key={index} xs={6} onClick={() => setSelectedImage(image)}>
              <Image
                name={image.title}
                description={image.description}
                isSelected={selectedImage?.id === image.id}
              />
            </Grid>
          ))}
        </Grid>
        <Button
          color={'primary'}
          variant={'contained'}
          className={classes.button}
          onClick={startSession(state, enqueueSnackbar)}
        >
          {loading ? <CircularProgress size={24} color={'white'} />: (
            <p>
              {!session ? 'Launch Playground' : 'Go to Playground'}
            </p>
          )}
        </Button>
      </Paper>
    </StandardLayout>
  );
}
