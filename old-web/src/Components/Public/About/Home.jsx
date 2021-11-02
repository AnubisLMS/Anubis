import React, {useState, useEffect, useRef} from 'react';
import {Link} from 'react-router-dom';


import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Scrambler from 'scrambling-text';

import HomeLayout from '../../Layouts/HomeLayout';

const useStyles = makeStyles((theme) => ({
  title: {
    position: 'absolute',
    [theme.breakpoints.down('md')]: {
      top: 20,
    },
    [theme.breakpoints.up('md')]: {
      top: 70,
    },
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
  logo: {
    margin: theme.spacing(5, 0),
    height: 256,
    width: 256,
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
    scramblerRef.current.scramble(titles[0], setText);
  }, []);

  useEffect(() => {
    setTimeout(() => {
      const nextIndex = (index + 1) % titles.length;
      scramblerRef.current.scramble(titles[nextIndex], setText);
      setIndex(nextIndex);
    }, 5000);
  }, [index]);

  return (
    <HomeLayout>
      <div className={classes.title}>
        <Typography color="inherit" align="center" variant="h2">
          {text}
        </Typography>
      </div>

      <img
        alt={'anubis-logo'}
        src={'/logo512.png'}
        className={classes.logo}
      />

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
