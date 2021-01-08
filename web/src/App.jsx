import React, {useState} from 'react';

import {BrowserRouter as Router, Redirect, Route} from 'react-router-dom';

import {SnackbarProvider} from 'notistack';

import clsx from 'clsx';

import {makeStyles, ThemeProvider} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import theme from './theme';
import MainSwitch from './Navigation/MainSwitch';
import useQuery from './hooks/useQuery';
import Nav from './Navigation/Nav';
import Error from './Components/Error';
import {drawerWidth} from './Navigation/navconfig';
import Footer from './Components/Footer';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    height: '100%',
    width: '100%',
    backgroundImage: `url(/curvylines.png)`,
    // flexDirection: 'column',
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: 'flex-end',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(6, 4),
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -drawerWidth,
  },
  main: {
    width: '100%',
    height: '100%',
    flexDirection: 'column',
    // background: '#eaeff1',
  },
  contentShift: {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
  footer: {
    padding: theme.spacing(2),
    bottom: '0',
    left: '0',
    textAlign: 'center',
    position: 'fixed',
    width: '100%',
  },
  chip: {
    padding: theme.spacing(1),
    width: '100%',
    textAlign: 'center',
  },
}));

export default function App() {
  const classes = useStyles();
  const query = useQuery();
  const [open, setOpen] = useState(true);
  const [showError, setShowError] = useState(!!query.get('error'));

  return (
    <ThemeProvider theme={theme}>
      <div className={classes.root}>
        <SnackbarProvider maxSnack={5}>
          <Router>
            <CssBaseline>
              <Route exact path={'/'}>
                <Redirect to={'/about'}/>
              </Route>

              <Nav
                variant="temporary"
                open={open}
                onClose={() => setOpen(false)}
                onOpen={() => setOpen(true)}
              />

              <main
                className={clsx(classes.content, classes.main, {
                  [classes.contentShift]: open,
                })}
              >
                <Error show={showError} onDelete={() => setShowError(false)}/>
                <MainSwitch/>

                <Footer/>
              </main>
            </CssBaseline>
          </Router>
        </SnackbarProvider>
      </div>
    </ThemeProvider>
  );
}
