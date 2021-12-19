import React, {useState, useEffect} from 'react';
import clsx from 'clsx';

import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import {makeStyles} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';

import StandardLayout from '../../Components/Layouts/StandardLayout';

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
    border: `1px solid ${theme.palette.primary.main}`,
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

  const Image = ({name, label, description, isSelected}) => {
    return (
      <Box className={!isSelected ? classes.image : clsx(classes.image, classes.selectedImage)}>
        <Box className={classes.imageHeader}>
          <h1>{name}</h1>
          <p className={classes.imageLabel}>{label}</p>
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
          {availableImages && availableImages.map((image, index) => (
            <Grid item key={index} xs={6} onClick={() => setSelectedImage(image.name)}>
              <Image
                name={image.name}
                label={image.label}
                description={image.description}
                isSelected={selectedImage === image.name}
              />
            </Grid>
          ))}
        </Grid>
        <Button
          color={'primary'}
          variant={'contained'}
          className={classes.button}
        >
          Launch Playground
        </Button>
      </Paper>
    </StandardLayout>
  );
}
