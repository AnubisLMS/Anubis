import React, {useState, useEffect, useRef} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Scrambler from 'scrambling-text';

import HomeLayout from '../../Layouts/HomeLayout';
import {Link} from 'react-router-dom';

const backgroundImage = '/logo512.png';

const useStyles = makeStyles((theme) => ({
  background: {
    backgroundImage: `url(${backgroundImage})`,
    // backgroundColor: '#7fc7d9', // Average color of the background image.
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


const titles = [
  'Automate your Course',
  'Eliminate class VMs',
  'Speed up grading',
  'Live feedback before the deadline',
  'Get insights into comprehension',
  'Powerful course management',
];

export default function Home() {
  const classes = useStyles();

  const [index, setIndex] = useState(0);
  const [text, setText] = useState(titles[0]);

  // create an instance of Scrambler using useRef.
  const scramblerRef = useRef(new Scrambler());

  useEffect(() => {
    if (window.innerWidth <= 960) {
      setText(titles[0]);
      return;
    }
    scramblerRef.current.scramble(titles[0], setText);
  }, []);

  useEffect(() => {
    if (window.innerWidth <= 960) {
      return;
    }
    setTimeout(() => {
      const nextIndex = (index + 1) % titles.length;
      scramblerRef.current.scramble(titles[nextIndex], setText);
      setIndex(nextIndex);
    }, 5000);
  }, [index]);

  return (
    <HomeLayout backgroundClassName={classes.background}>
      <Typography color="inherit" align="center" variant="h2" marked="center" display={'inline'}>
        {text}
      </Typography>
      <Typography color="inherit" align="center" variant="h5" className={classes.h5}>
        Simplify your CS Course with Anubis
      </Typography>
      <Button
        color="primary"
        variant="contained"
        size="large"
        className={classes.button}
        component={Link}
        to={'/blog/elevator-pitch'}
      >
        Find out more
      </Button>
    </HomeLayout>
  );
}
