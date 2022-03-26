import React, {useState} from 'react';
import clsx from 'clsx';

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
import AuthContext from './context/AuthContext';

// Navconfig
import {drawerWidth} from './navconfig';

// Dark theme
import theme from './theme/Theme';

import AuthWrapper from './components/shared/AuthWrapper';
import Main from './Main';
import Forums from './containers/Forums/Forums';
import Nav from './components/shared/Navigation/Nav';
import Error from './components/shared/Error';
import Footer from './components/shared/Footer';
import Header from './components/shared/Header';
import DeviceWarning from './components/shared/DeviceWarning';

import 'devicon/devicon.min.css';

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
  logInButton: {
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
  const [open, setOpen] = useState(window.innerWidth >= 960); // 960px is md

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
                        <div className={classes.drawerHeader}/>
                        <Error/>
                        <div className={classes.main}>
                          <Main user={user}/>
                          <Forums user={user}/>
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
      </div>
    </ThemeProvider>
  );
}
