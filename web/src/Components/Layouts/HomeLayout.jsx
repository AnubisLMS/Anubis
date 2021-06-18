import React from 'react';
import clsx from 'clsx';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import IconButton from '@material-ui/core/IconButton';


const useStyles = makeStyles((theme) => ({
  root: {
    color: theme.palette.common.white,
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
  logo: {
    margin: theme.spacing(5),
    height: 256,
    width: 256,
  },
}));


export default function HomeLayout({children = null}) {
  const classes = useStyles();

  return (
    <section className={classes.root}>
      <Container className={classes.container}>
        <img
          alt={'anubis-logo'}
          src={'/logo512.png'}
          className={classes.logo}
        />
        {children}

        <IconButton
          color={'primary'}
          className={classes.arrowDown}
          href={'#values'}
        >
          <ArrowDownwardIcon/>
        </IconButton>

      </Container>
    </section>
  );
}

