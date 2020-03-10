import React from 'react';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {useSnackbar} from 'notistack';
import {green} from '@material-ui/core/colors';

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

export default function Build({data}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  if (!data) {
    return (
      <div/>
    );
  } else {
    enqueueSnackbar('Build succeeded', {variant: 'success'});
  }

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant="h5" component="h2">
          Build Logs
        </Typography>
        {data ? data.trim().split('\n').map(line => (
          <Typography
            className={classes.pos}
            // component="pre"
            variant={"body1"}
            color={"textSecondary"}
            width={100}
          >
            {line}
          </Typography>
        )) : null}
      </CardContent>
    </Card>
  )
}