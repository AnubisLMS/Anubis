import React from 'react';
import PropTypes from 'prop-types';
import {createMuiTheme, ThemeProvider, withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Hidden from '@material-ui/core/Hidden';
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import {BrowserRouter as Router, Route, Switch} from "react-router-dom";
import {SnackbarProvider} from 'notistack';

import Navigator from './Navigator';
import View from './View';
import SearchSubmissions from "./SearchSubmissions";

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="primay" href={
        (process.env.REACT_APP_DEV ?
          'https://api.localhost/public/credits' :
          'https://api.nyu.cool/public/credits'
        )
      }>
        NYU OS 3224
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

let theme = createMuiTheme({
  palette: {
    primary: {
      light: '#63ccff',
      main: '#009be5',
      dark: '#006db3',
    },
    type: "dark"
  },
  typography: {
    h5: {
      fontWeight: 500,
      fontSize: 26,
      letterSpacing: 0.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  props: {
    MuiTab: {
      disableRipple: true,
    },
  },
  mixins: {
    toolbar: {
      minHeight: 48,
    },
  },
});

theme = {
  ...theme,
  overrides: {
    MuiDrawer: {
      paper: {
        backgroundColor: '#18202c',
      },
    },
    MuiButton: {
      label: {
        textTransform: 'none',
      },
      contained: {
        boxShadow: 'none',
        '&:active': {
          boxShadow: 'none',
        },
      },
    },
    MuiTabs: {
      root: {
        marginLeft: theme.spacing(1),
      },
      indicator: {
        height: 3,
        borderTopLeftRadius: 3,
        borderTopRightRadius: 3,
        backgroundColor: theme.palette.common.white,
      },
    },
    MuiTab: {
      root: {
        textTransform: 'none',
        margin: '0 16px',
        minWidth: 0,
        padding: 0,
        [theme.breakpoints.up('md')]: {
          padding: 0,
          minWidth: 0,
        },
      },
    },
    MuiIconButton: {
      root: {
        padding: theme.spacing(1),
      },
    },
    MuiTooltip: {
      tooltip: {
        borderRadius: 4,
      },
    },
    MuiDivider: {
      root: {
        backgroundColor: '#404854',
      },
    },
    MuiListItemText: {
      primary: {
        fontWeight: theme.typography.fontWeightMedium,
      },
    },
    MuiListItemIcon: {
      root: {
        color: 'inherit',
        marginRight: 0,
        '& svg': {
          fontSize: 20,
        },
      },
    },
    MuiAvatar: {
      root: {
        width: 32,
        height: 32,
      },
    },
  },
};

const drawerWidth = 256;

const styles = {
  root: {
    display: 'flex',
    width: '100%',
    minHeight: '100vh',
  },
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  app: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    width: '100%'
  },
  main: {
    flex: 1,
    padding: theme.spacing(6, 4),
    width: '100%'
    // background: '#eaeff1',
  },
  footer: {
    padding: theme.spacing(2),
    // background: '#eaeff1',
  },
};

function Paperbase(props) {
  const {classes} = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <div className={classes.root}>
        <SnackbarProvider maxSnack={5}>
          <Router>
            <CssBaseline/>
            <nav className={classes.drawer}>
              <Hidden smUp implementation="js">
                <Navigator
                  PaperProps={{style: {width: drawerWidth}}}
                  variant="temporary"
                  open={mobileOpen}
                  onClose={handleDrawerToggle}
                />
              </Hidden>
              <Hidden xsDown implementation="css">
                <Navigator PaperProps={{style: {width: drawerWidth}}}/>
              </Hidden>
            </nav>
            <div className={classes.app}>
              <main className={classes.main}>
                <SearchSubmissions/>
                <Switch>
                  <Route exact path={'/view/:commit'}>
                    <View/>
                  </Route>
                  <Route exact path={'/view/:commit/:netid'}>
                    <View/>
                  </Route>
                </Switch>
              </main>
              <footer className={classes.footer}>
                <Copyright/>
              </footer>
            </div>
          </Router>
        </SnackbarProvider>
      </div>
    </ThemeProvider>
  );
}

Paperbase.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(Paperbase);
