import React, {useState} from 'react';

import {BrowserRouter as Router} from 'react-router-dom';
import {SnackbarProvider} from 'notistack';
import clsx from 'clsx';

import {makeStyles, ThemeProvider} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import {drawerWidth} from './Navigation/navconfig';
import theme from './Theme/Dark';

import AuthContext from './Contexts/AuthContext';

import AuthWrapper from './Components/AuthWrapper';
import Main from './Main';
import useQuery from './hooks/useQuery';
import Nav from './Navigation/Nav';
import Error from './Components/Error';
import Footer from './Components/Footer';
import Header from './Components/Header';
import DeviceWarning from './Components/DeviceWarning';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    height: '100%',
    minHeight: '100vh',
    width: '100%',
    backgroundImage: `url(/curvylines.png)`,
    backgroundRepeat: 'repeat',
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
    flexDirection: 'column',
    marginBottom: theme.spacing(5),
  },
  contentShift: {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
  app: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
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
          <DeviceWarning/>
          <Router>
            <AuthWrapper>
              <AuthContext.Consumer>
                {(user) => (
                  <CssBaseline>
                    <Nav
                      variant="temporary"
                      open={open}
                      onDrawerToggle={() => setOpen((prev) => !prev)}
                    />
                    <div className={classes.app} id={'app'}>
                      <Header
                        onDrawerToggle={() => setOpen((prev) => !prev)}
                        user={user}
                      />
                      <main
                        className={clsx(classes.content, classes.main, {
                          [classes.contentShift]: open,
                        })}
                      >
                        <Error show={showError} onDelete={() => setShowError(false)}/>
                        <Main user={user}/>
                        <Footer/>
                      </main>
                    </div>
                  </CssBaseline>
                )}
              </AuthContext.Consumer>
            </AuthWrapper>
          </Router>
        </SnackbarProvider>
      </div>
    </ThemeProvider>
  );
}
