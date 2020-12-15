import React, {useState} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import {makeStyles, ThemeProvider, withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import Chip from '@material-ui/core/Chip';
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
import IDE from "./Pages/IDE/View";
import Repos from "./Pages/Repos/View";
import theme from './theme';
import {useQuery} from './utils';
import Profile from "./Pages/Profile/View";

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
  chip: {
    padding: theme.spacing(1),
    width: "100%",
    textAlign: "center",
  }
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
              <Navigator
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
                <div className={classes.drawerHeader}/>

                {showError
                  ? <div className={classes.chip}>
                    <Chip
                      label={query.get('error')}
                      onDelete={() => setShowError(false)}
                      color="secondary"
                    />
                  </div>
                  : null}

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

                  {/* Theia IDE */}
                  <Route exact path={'/ide'}>
                    <IDE/>
                  </Route>

                  {/* Repo view */}
                  <Route exact path={'/repos'}>
                    <Repos/>
                  </Route>

                  {/* Profile view */}
                  <Route exact path={'/profile'}>
                    <Profile/>
                  </Route>

                  {/* Set github username */}
                  <Route exact path={'/set-github-username'}>
                    <GetGithubUsername/>
                  </Route>

                  {/* About */}
                  <Route exact path={"/about"}>
                    <About/>
                  </Route>

                  {/* Authentication */}
                  <Route exact path={'/logout'}>
                    <Redirect to={'/api/public/logout'} push/>
                  </Route>

                  {/* 404 Not Found */}
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
