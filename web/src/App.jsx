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
  main: {
    width: '100%',
    flexDirection: 'column',
    padding: theme.spacing(6, 4),
    marginBottom: theme.spacing(5),
  },
  app: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
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
}));

export default function App() {
  const classes = useStyles();
  const query = useQuery();
  const [open, setOpen] = useState(window.innerWidth >= 960); // 960px is md
  const [showError, setShowError] = useState(!!query.get('error'));

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };


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
                      classes={classes}
                      open={open}
                      handleDrawerClose={handleDrawerClose}
                    />
                    <div className={classes.app} id={'app'}>
                      <Header
                        onDrawerToggle={() => setOpen((prev) => !prev)}
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
