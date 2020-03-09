import React, {useState} from 'react';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import {makeStyles} from '@material-ui/core/styles';
import CheckIcon from '@material-ui/icons/Check';
import CloseIcon from '@material-ui/icons/Close';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import {Redirect, useParams} from "react-router-dom";
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import {useSnackbar} from 'notistack';
import CircularProgress from "@material-ui/core/CircularProgress";
import {green} from '@material-ui/core/colors';

import {api} from './utils';

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

function Auth(props) {
  const classes = useStyles();
  const [netid, setNetid] = useState('');
  const {
    open,
    onClose,
    setData,
    commit,
    setProcessed,
    timer
  } = props;

  const handler = res => {
    if (res.data && res.data.success) {
      const {submission} = res.data.data;
      const {processed} = submission;
      setProcessed(processed);
      if (processed) clearInterval(timer.current);
    }
    setData(res.data);
  };

  const verify = () => {
    api.get(`/submissions/${commit}/${netid}`).then(res => {
      if (res.data && res.data.success) {
        timer.current = setInterval(() => (
          api.get(`/submissions/${commit}/${netid}`).then(handler)
        ), 5000);
        handler(res);
      }
    }).catch(err => null);
  };

  return (
    <Dialog open={open} onClose={onClose} className={classes.dialog}>
      <DialogTitle>
        Verification
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          Please verify your netid to see the submission data for <br/>{commit}
        </DialogContentText>
        <TextField
          required
          autoFocus
          fullWidth
          margin={'dense'}
          variant={'outlined'}
          label={'netid'}
          onChange={e => setNetid(e.target.value)}
          onKeyPress={e => e.key === 'Enter' ? verify() : null}
        />
      </DialogContent>
      <DialogActions>
        <Button variant="contained" color="primary" onClick={verify}>
          Verify
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function Submission({data, processed}) {
  const classes = useStyles();
  if (!data) return <div/>;
  const {assignment, commit, timestamp} = data;

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h6'} component={'h2'}>
          {`${assignment} Submission`}
        </Typography>
        <Typography className={classes.pos} color="textSecondary">
          {timestamp}
        </Typography>
        <Typography color="textSecondary">
          {commit}
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              {
                processed ? (
                  <Tooltip title={'processed'}>
                    <IconButton>
                      <CheckIcon color={'primary'}/>
                    </IconButton>
                  </Tooltip>
                ) : (
                  <IconButton>
                    <Tooltip title={'processing'}>
                      <CircularProgress color={"primary"}/>
                    </Tooltip>
                  </IconButton>
                )
              }
            </ListItemIcon>
            <ListItemText primary={processed ? 'processed' : 'processing'}/>
          </ListItem>
        </List>
      </CardContent>
    </Card>
  );
}

function Reports({data}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  if (!data) {
    enqueueSnackbar('Test error', {variant: 'error'});
    return (
      <div/>
    )
  } else {
    for (const r of data) {
      enqueueSnackbar(
        `${r.testname} ${r.passed ? 'passed' : 'failed'}`,
        {variant: r.passed ? 'success' : 'error'}
      )
    }
  }

  return (
    <Card className={classes.card}>
      <CardContent>
        <List className={classes.list}>
          {data.map(({testname, passed, errors}) => (
            <ListItem>
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
      </CardContent>
    </Card>
  );
}

function Build({data}) {
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
        <Typography
          className={classes.pos}
          component="pre"
          color={"textSecondary"}
        >
          {data ? data.trim() : null}
        </Typography>
      </CardContent>
    </Card>
  )
}

function Tests({data}) {
  const classes = useStyles();
  if (!data) {
    return (
      <div/>
    );
  }
  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant="h5" component="h2">
          Test Logs
        </Typography>
        <Typography
          className={classes.pos}
          component="pre"
          color={"textSecondary"}
        >
          {data ? data.trim() : null}
        </Typography>
      </CardContent>
    </Card>
  );
}

function Error({data}) {
  const classes = useStyles();

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant={'h5'} component={'h3'}>
          Error
        </Typography>
        <Typography variant={"body2"} color={"textSecondary"}>
          {data}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function View() {
  const [data, setData] = useState(null);
  const [authOpen, setAuth] = useState(true);
  const [processed, setProcessed] = React.useState(true);
  const {commit} = useParams();
  const {enqueueSnackbar} = useSnackbar();
  const timer = React.useRef();

  React.useEffect(() => {
    return () => {
      clearInterval(timer.current);
    };
  }, []);

  if (data === null) return (
    <Auth
      open={authOpen}
      onClose={() => setAuth(false)}
      setData={setData}
      commit={commit}
      setProcessed={setProcessed}
      timer={timer}
    />
  );

  let submission, reports, build, tests, errors;

  if (data.success) {
    submission = data.data.submission;
    reports = data.data.reports;
    build = data.data.build;
    tests = data.data.tests;
    errors = data.data.errors;
  }

  if (!data.success) {
    enqueueSnackbar(data.error, {variant: 'error'});
    return (
      <Redirect to={'/'}/>
    );
  }

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <Submission
          data={submission}
          processed={processed}
        />
      </Grid>
      {processed && !errors ? (
        <React.Fragment>
          <Grid item xs={12} sm={6}>
            <Reports data={reports}/>
          </Grid>
          <Grid item xs={12}>
            <Tests data={tests}/>
          </Grid>
          <Grid item xs={12}>
            <Build data={build}/>
          </Grid>
        </React.Fragment>
      ) : (
        <Grid item xs={12}>
          <Error data={errors}/>
        </Grid>
      )}
    </Grid>
  );
}
