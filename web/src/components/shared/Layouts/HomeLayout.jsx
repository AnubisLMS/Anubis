import React from 'react';
import {Link as SmoothLink, animateScroll as scroll} from 'react-scroll';

import makeStyles from '@mui/material/styles/makeStyles';
import Container from '@mui/material/Container';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import IconButton from '@mui/material/IconButton';


const useStyles = makeStyles((theme) => ({
  root: {
    color: theme.palette.white,
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    [theme.breakpoints.up('sm')]: {
      height: '80vh',
      minHeight: 500,
      maxHeight: 1300,
    },
  },
  container: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(14),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  arrowDown: {
    position: 'absolute',
    bottom: theme.spacing(4),
  },
  icon: {
    fontSize: 128,
  },
}));


export default function HomeLayout({children = null}) {
  const classes = useStyles();

  return (
    <section className={classes.root}>
      <Container className={classes.container}>
        {children}
        <IconButton
          color={'primary'}
          className={classes.arrowDown}
          component={SmoothLink}
          to={'values'}
          activeClass="active"
          smooth={true}
          offset={-70}
          duration={500}
        >
          <ArrowDownwardIcon fontSize={'large'}/>
        </IconButton>

      </Container>
    </section>
  );
}

