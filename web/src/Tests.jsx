import React from 'react';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import CheckIcon from '@material-ui/icons/Check';
import CloseIcon from '@material-ui/icons/Close';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {useSnackbar} from 'notistack';
import {makeStyles} from "@material-ui/core/styles";
import {green} from "@material-ui/core/colors";

const useStyles = makeStyles(theme => ({
  paper: {
    maxWidth: 936,
    margin: theme.spacing(2),
    padding: theme.spacing(2),
    overflow: 'hidden',
  },
  searchBar: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  searchInput: {
    fontSize: theme.typography.fontSize,
  },
  title: {
    fontSize: 14,
  },
  block: {
    display: 'block',
  },
  addUser: {
    marginRight: theme.spacing(1),
  },
  contentWrapper: {
    margin: '40px 16px',
  },
  card: {
    minWidth: 275,
  },
  list: {
    width: '100%',
  },
  dialog: {
    margin: theme.spacing(2),
    padding: theme.spacing(2)
  },
  closeButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
  progress: {
    padding: theme.spacing(1)
  },
  fabProgress: {
    color: green[500],
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
  buttonProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
}));

export default function Tests({tests, reports}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  if (!tests || !reports) {
    return (
      <div/>
    );
  } else {
    for (const r of reports) {
      enqueueSnackbar(
        `${r.testname} ${r.passed ? 'passed' : 'failed'}`,
        {variant: r.passed ? 'success' : 'error'}
      )
    }
  }
  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant="h5" component="h2">
          Tests
        </Typography>
        <List className={classes.list}>
          {reports.map(({testname, passed, errors}) => (
            <ListItem key={testname}>
              <ListItemIcon>
                {passed ? (
                  <Tooltip title={
                    (JSON.parse(errors).length > 0) ? JSON.parse(errors)[0] : 'passed'
                  }>
                    <IconButton>
                      <CheckIcon color={'primary'}/>
                    </IconButton>
                  </Tooltip>
                ) : (
                  <Tooltip title={
                    (JSON.parse(errors).length > 0) ? JSON.parse(errors)[0] : 'failed'
                  }>
                    <IconButton>
                      <CloseIcon color={'secondary'}/>
                    </IconButton>
                  </Tooltip>
                )}
              </ListItemIcon>
              <ListItemText primary={testname}/>
            </ListItem>
          ))}
        </List>
        <Typography variant={'h5'} component={'h2'}>
          Logs
        </Typography>
        <Typography
          className={classes.pos}
          component="pre"
          color={"textSecondary"}
        >
          {tests ? tests.trim() : null}
        </Typography>
      </CardContent>
    </Card>
  );
}