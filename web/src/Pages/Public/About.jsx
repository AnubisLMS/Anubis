import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Home from '../../Components/Public/About/Home';
import Values from '../../Components/Public/About/Values';

const useStyles = makeStyles((theme) => ({
  background: {
    // backgroundImage: `url(${backgroundImage})`,
    backgroundColor: '#7fc7d9', // Average color of the background image.
    backgroundPosition: 'center',
  },
  button: {
    minWidth: 200,
  },
  h5: {
    marginBottom: theme.spacing(4),
    marginTop: theme.spacing(4),
    [theme.breakpoints.up('sm')]: {
      marginTop: theme.spacing(10),
    },
  },
  more: {
    marginTop: theme.spacing(2),
  },
}));


export default function About() {
  const classes = useStyles();

  return (
    <div>
      <Home/>
      <Values/>
    </div>
  );
}
