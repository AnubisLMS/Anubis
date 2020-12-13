import React, {useState} from "react";
import clsx from "clsx";
import {makeStyles, useTheme} from "@material-ui/core/styles";
import Drawer from "@material-ui/core/Drawer";
import CssBaseline from "@material-ui/core/CssBaseline";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import ChevronRightIcon from "@material-ui/icons/ChevronRight";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import SchoolIcon from "@material-ui/icons/School";
import AssignmentOutlinedIcon from "@material-ui/icons/AssignmentOutlined";
import ExitToAppOutlinedIcon from "@material-ui/icons/ExitToAppOutlined";
import PublicIcon from "@material-ui/icons/Public";
import AssessmentIcon from '@material-ui/icons/Assessment';
import CloseOutlinedIcon from '@material-ui/icons/CloseOutlined';
import LaunchOutlinedIcon from '@material-ui/icons/LaunchOutlined';
import CodeOutlinedIcon from '@material-ui/icons/CodeOutlined';
import {Link} from "react-router-dom";


const categories = [
  {
    id: "Courses",
    icon: <SchoolIcon/>,
    path: "/courses"},
  {
    id: "Assignments",
    icon: <AssignmentOutlinedIcon/>,
    path: "/courses/assignments"
  },
  {
    id: "Submissions",
    icon: <AssessmentIcon/>,
    path: "/courses/assignments/submissions"
  },
  {
    id: "Anubis IDE",
    icon: <CodeOutlinedIcon/>,
    path: "/ide"
  }
];

const footerLinks = [
  {id: "About", icon: <PublicIcon/>, path: "/about"},
];
const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex"
  },
  appBar: {
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    })
  },
  appBarShift: {
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: drawerWidth,
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen
    })
  },
  menuButton: {
    marginRight: theme.spacing(2)
  },
  hide: {
    display: "none"
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0
  },
  drawerPaper: {
    width: drawerWidth
  },
  drawerHeader: {
    display: "flex",
    alignItems: "center",
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
    justifyContent: "flex-end"
  },
  drawerIcon: {
    marginLeft: 75
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
  bottomPush: {
    // position: "absolute",
    bottom: 0,
    display: "inline",
    paddingBottom: 10,
  },
  drawerHeaderText: {
    marginTop: 5
  }
}));

export default function Navigator(props) {
  const classes = useStyles();
  const {open, onClose, onOpen} = props;
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const theme = useTheme();

  const updatePath = path => () => setCurrentPath(path);

  return (
    <div className={classes.root}>
      <CssBaseline/>
      <AppBar
        position="fixed"
        color="inherit"
        className={clsx(classes.appBar, {
          [classes.appBarShift]: open
        })}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={onOpen}
            edge="start"
            className={clsx(classes.menuButton, open && classes.hide)}
          >
            <MenuIcon/>
          </IconButton>
        </Toolbar>
      </AppBar>
      <Drawer
        className={classes.drawer}
        variant="persistent"
        anchor="left"
        open={open}
        classes={{
          paper: classes.drawerPaper
        }}
      >
        <div className={classes.drawerHeader}>
          <div className={classes.drawerHeaderText}>
            <Typography variant="h5">Anubis </Typography>
          </div>
          <div className={classes.drawerIcon}>
            <IconButton onClick={onClose}>
              {theme.direction === "ltr" ? (
                <ChevronLeftIcon/>
              ) : (
                <ChevronRightIcon/>
              )}
            </IconButton>
          </div>
        </div>
        <Divider/>
        <List>
          {categories.map(({id, icon, path}) => (
            <ListItem button key={id}
                      component={Link}
                      to={path}
                      selected={currentPath === path}
                      onClick={updatePath(path)}
            >
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={id}/>
            </ListItem>
          ))}
        </List>
        <div className={classes.bottomPush}>
          <List>
            {footerLinks.map(({id, icon, path}) => (
              <ListItem button key={id}
                        component={Link}
                        to={path}
                        selected={currentPath === path}
                        onClick={updatePath(path)}
              >
                <ListItemIcon>{icon}</ListItemIcon>
                <ListItemText primary={id}/>
              </ListItem>
            ))}
            <ListItem button key="Login"
                      component={"a"}
                      href={"/api/public/login"}
            >
              <ListItemIcon><ExitToAppOutlinedIcon/></ListItemIcon>
              <ListItemText primary={"Login"}/>
            </ListItem>
            <ListItem button key="Logout"
                      component={"a"}
                      href={"/api/public/logout"}>
              <ListItemIcon><LaunchOutlinedIcon/></ListItemIcon>
              <ListItemText primary={"Logout"}/>
            </ListItem>
          </List>
        </div>
      </Drawer>

    </div>
  );
}


