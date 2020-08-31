import React, {useState} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import {createMuiTheme, ThemeProvider, withStyles, useTheme, makeStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Hidden from '@material-ui/core/Hidden';
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import {BrowserRouter as Router, Redirect, Route, Switch} from "react-router-dom";
import {SnackbarProvider} from 'notistack';
import CourseView from './Pages/Courses/View';
import AssignmentView from './Pages/Assignments/View'
import Navigator from './Navigation/Navigator';
//import SubmissionView from './Submissions/View';
//import SearchSubmissions from "./Submissions/SearchSubmissions";
import NotFound from "./NotFound";
import apiUrl from './utils';
import { Toolbar } from '@material-ui/core';


let theme = createMuiTheme({
  palette: {
    primary: {
      light: "#63ccff",
      main: "#009be5",
      dark: "#006db3"
      
    },
    type: "dark"
  },

  typography: {
    h5: {
      fontWeight: 300,
      fontSize: 30,
      letterSpacing: 0.7
    }
  },
  shape: {
    borderRadius: 8
  },
  props: {
    MuiTab: {
      disableRipple: true
    }
  },
  mixins: {
    toolbar: {
      minHeight: 48,
 
    }
  }
});

theme = {
  ...theme,
  overrides: {
    MuiDrawer: {
      paper: {
        backgroundColor: "#18202c"
      }, 
    },
    MuiButton: {
      label: {
        textTransform: "none"
      },
      contained: {
        boxShadow: "none",
        "&:active": {
          boxShadow: "none"
        }
      }
    },
    MuiTabs: {
      root: {
        marginLeft: theme.spacing(1)
      },
      indicator: {
        height: 3,
        borderTopLeftRadius: 3,
        borderTopRightRadius: 3,
        backgroundColor: theme.palette.common.white
      }
    },
    MuiTab: {
      root: {
        textTransform: "none",
        margin: "0 16px",
        minWidth: 0,
        padding: 0,
        [theme.breakpoints.up("md")]: {
          padding: 0,
          minWidth: 0
        }
      }
    },
    MuiIconButton: {
      root: {
        padding: theme.spacing(1)
      }
    },
    MuiTooltip: {
      tooltip: {
        borderRadius: 4
      }
    },
    MuiDivider: {
      root: {
        backgroundColor: "#404854"
      }
    },
    MuiListItemText: {
      primary: {
        fontWeight: theme.typography.fontWeightMedium
      }
    },
    MuiListItemIcon: {
      root: {
        color: "inherit",
        marginRight: -7,
        "& svg": {
          fontSize: 20
        }
      }
    },
    MuiAvatar: {
      root: {
        width: 32,
        height: 32
      }
    }
  }
};
const drawerWidth = 240;
const useStyles = makeStyles(() =>({
  root: {
    display: 'flex',

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
    padding: theme.spacing(3),
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    marginLeft: -drawerWidth
  },
  contentShift: {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen
    }),
    marginLeft: 0
  },
}));

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link href={apiUrl + '/public/memes'}>
        Memes
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

function App(props) {
  const classes = useStyles();
  const [data, setData] = useState(null);
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
            <Route exact path ={'/'}>
              <Redirect to={'/courses'}/>
            </Route>
            <Navigator              
              variant="temporary"
              open={open}
              onClose={handleDrawerClose}
              onOpen={handleDrawerOpen}
            />
            <main 
            className={clsx(classes.content, {
            [classes.contentShift]: open,
            })}
          >
          <div className={classes.drawerHeader} />
          <Switch>
             {/* Courses page */}
            <Route exact path = {'/courses'} >     
              <CourseView />    
               
              </Route>
                {/* Assignments page */}
                <Route exact path = {'/courses/:courseid/assignments'}>
                    <AssignmentView />
                </Route>

                {/* Submissions page */}
                <Route exact path = {'/courses/:courseid/assignments/:assignmentid/submissions'}>                  
                </Route>
                
                {/* Individual submission status, test results page  */}
                <Route exact path = {'/courses/:courseid/assignments/:assignmentid/submissions/:commit'}>
                </Route>
           
            
            <Route>
              <div className={classes.app}>
                <main className={classes.main}>
                  <NotFound/>
                </main>
              </div>
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
