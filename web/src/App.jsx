import React, {useState} from 'react';
import clsx from 'clsx';

// useSWR
import {SWRConfig} from 'swr';
import axios from 'axios';

// React router
import {BrowserRouter as Router} from 'react-router-dom';

// Snackbar
import {SnackbarProvider} from 'notistack';

// React vis stylesheet
import 'react-vis/dist/style.css';

import {ThemeProvider} from '@material-ui/core/styles';
import makeStyles from '@material-ui/core/styles/makeStyles';
import CssBaseline from '@material-ui/core/CssBaseline';

// Auth Context
import AuthContext from './Contexts/AuthContext';

// Navconfig
import {drawerWidth} from './navconfig';

// Dark theme
import theme from './Theme/Theme';

import AuthWrapper from './Components/AuthWrapper';
import Main from './Main';
import useQuery from './hooks/useQuery';
import Nav from './Components/Navigation/Nav';
import Error from './Components/Error';
import Footer from './Components/Footer';
import Header from './Components/Header';
import DeviceWarning from './Components/DeviceWarning';
import Container from '@material-ui/core/Container';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    height: '100%',
    minHeight: '100vh',
    // width: '100%',
    backgroundColor: theme.palette.dark.black,
  },
  app: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  githubButton: {
    margin: theme.spacing(2, 1),
  },
  content: {
    marginTop: theme.spacing(6),
    flexGrow: 1,
    // padding: theme.spacing(3),
    marginBottom: '20px',
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginLeft: -drawerWidth,
  },
  contentShift: {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  },
  menuButton: {
    marginLeft: -theme.spacing(1),
  },
  avatar: {
    'display': 'flex',
    '& > *': {
      margin: theme.spacing(1),
    },
  },
  appBar: {
    // height: 50,
    backgroundColor: theme.palette.dark.blue['200'],
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  appBarChip: {
    backgroundColor: theme.palette.primary.main,
  },
  main: {
    [theme.breakpoints.up('sm')]: {
      padding: theme.spacing(2),
    },
  },
}));

export default function App() {
  const classes = useStyles();
  const query = useQuery();
  const [open, setOpen] = useState(window.innerWidth >= 960); // 960px is md
  const [showError, setShowError] = useState(!!query.get('error'));

  return (
    <ThemeProvider theme={theme}>
      <div className={classes.root}>
        <SWRConfig
          value={{
            shouldRetryOnError: false,
            fetcher: (...args) => fetch(...args).then((res) => res.json()).catch((error) => {
              if (error?.response?.status === 401) {
                window.location = '/api/public/auth/login';
              } else {
                throw error;
              }
            }),
          }}
        >
          <SnackbarProvider maxSnack={5}>
            <DeviceWarning/>
            <Router>
              <AuthWrapper>
                <AuthContext.Consumer>
                  {(user) => (
                    <CssBaseline>
                      <Nav
                        open={open}
                        handleDrawerClose={() => setOpen(!open)}
                      />
                      <div className={classes.app} id={'app'}>
                        <Header
                          onDrawerToggle={() => setOpen(!open)}
                          user={user}
                          classes={classes}
                          open={open}
                        />
                        <main
                          className={clsx(classes.content, {
                            [classes.contentShift]: open,
                          })}
                        >
                          <div className={classes.drawerHeader} />
                          <Error show={showError} onDelete={() => setShowError(false)}/>
                          <div className={classes.main}>
                            <Main user={user}/>
                          </div>
                          <Footer/>
                        </main>
                      </div>
                    </CssBaseline>
                  )}
                </AuthContext.Consumer>
              </AuthWrapper>
            </Router>
          </SnackbarProvider>
        </SWRConfig>
      </div>
    </ThemeProvider>
  );
}
