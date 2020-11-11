import React, {useState} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import {createMuiTheme, makeStyles, ThemeProvider, withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import {BrowserRouter as Router, Redirect, Route, Switch} from "react-router-dom";
import {SnackbarProvider} from 'notistack';
import CourseView from './Pages/Courses/View';
import AssignmentView from './Pages/Assignments/View'
import Navigator from './Navigation/Navigator';
import SubmissionInfo from './Pages/Submissions/Info/View';
import NotFound from "./NotFound";
import SubmissionsView from './Pages/Submissions/View';
import GetGithubUsername from "./Pages/GithubUsername/GetGithubUsername";
import About from "./Pages/About/About";
import Questions from "./Pages/Questions/View";
import theme from './theme';

const drawerWidth = 240;
const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    height: '100%',
    width: '100%',
    backgroundImage: `url(/curvylines.png)`,
    // flexDirection: 'column',
  },
  drawerHeader: {
    display: "flex",
    alignItems: "center",
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: "flex-end"
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(6, 4),
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    marginLeft: -drawerWidth
  },
  main: {
    width: '100%',
    height: '100%',
    flexDirection: 'column',
    // background: '#eaeff1',
  },
  contentShift: {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen
    }),
    marginLeft: 0
  },
  footer: {
    padding: theme.spacing(2),
    bottom: '0',
    left: '0',
    textAlign: "center",
    position: 'fixed',
    width: "100%",
    // background: '#eaeff1',
  },
}));

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link href={'/api/public/memes'}>
        Memes
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

function App() {
  const classes = useStyles();
  const [open, setOpen] = useState(true);
  const handleDrawerClose = () => {
    setOpen(false);
  };
  const handleDrawerOpen = () => {
    setOpen(true);
  };

  return (
    <ThemeProvider theme={theme}>
      <div className={classes.root}>
        <SnackbarProvider maxSnack={5}>
          <Router>
            <CssBaseline>
              <Route exact path={'/'}>
                <Redirect to={'/about'}/>
              </Route>
              <Navigator
                variant="temporary"
                open={open}
                onClose={handleDrawerClose}
                onOpen={handleDrawerOpen}
              />
              <main
                className={clsx(classes.content, classes.main, {
                  [classes.contentShift]: open,
                })}
              >
                <div className={classes.drawerHeader}/>
                <Switch style={{width: '100%'}}>
                  {/* Courses page */}
                  <Route exact path={'/courses'}>
                    <CourseView/>
                  </Route>
                  {/* Assignments page */}
                  <Route exact path={'/courses/assignments'}>
                    <AssignmentView/>
                  </Route>
                  <Route exact path={'/courses/assignments/submissions'}>
                    <SubmissionsView/>
                  </Route>
                  <Route exact path={'/courses/assignments/submissions/info'}>
                    <SubmissionInfo/>
                  </Route>
                  <Route exact path={'/courses/assignments/questions'}>
                    <Questions/>
                  </Route>
                  <Route exact path={'/set-github-username'}>
                    <GetGithubUsername/>
                  </Route>
                  <Route exact path={"/about"}>
                    <About/>
                  </Route>
                  <Route exact path={'/logout'}>
                    <Redirect to={'/api/public/logout'} push/>
                  </Route>
                  <Route>
                    <div className={classes.app}>
                      <main className={classes.main}>
                        <NotFound/>
                      </main>
                    </div>
                  </Route>
                </Switch>
                <Switch>
                  <Route exact path={'/about'}/>
                  <Route>
                    <footer className={classes.footer}>
                      {window.location.pathname !== '/about'
                        ? <Copyright/>
                        : null}
                    </footer>
                  </Route>
                </Switch>
              </main>
            </CssBaseline>
          </Router>
        </SnackbarProvider>
      </div>
    </ThemeProvider>
  );
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(useStyles)(App);
