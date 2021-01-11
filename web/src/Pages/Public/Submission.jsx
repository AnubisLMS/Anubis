import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Redirect} from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';
import green from '@material-ui/core/colors/green';
import {useSnackbar} from 'notistack';
import useSubscribe from '../../hooks/useSubscribe';
import axios from 'axios';
import useQuery from '../../hooks/useQuery';
import SubmissionSummary from '../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../Components/Public/Submission/SubmissionBuild';
import SubmissionTests from '../../Components/Public/Submission/SubmissionTests';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  heading: {
    padding: theme.spacing(2),
    display: 'flex',
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
  buttonSuccess: {
    'backgroundColor': green[500],
    '&:hover': {
      backgroundColor: green[700],
    },
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
}));

function regrade(commit, enqueueSnackbar) {
  axios
    .get(`/api/public/regrade/${commit}`)
    .then((response) => {
      if (response.data.success) {
        window.location.reload();
      } else {
        enqueueSnackbar(`Unable to regrade`, {variant: 'error'});
      }
    })
    .catch((error) => {
      enqueueSnackbar(`Unable to regrade`, {variant: 'error'});
    });
}


export default function Submission() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [{loading, error, data}] = useSubscribe(
    `/api/public/submissions/get/${useQuery().get('commit')}`,
    1000,
    (data) => data.submission.processed,
    (oldState, newState) => {
      if (oldState.data.submission === undefined) return;
      if (oldState.data.submission.build.passed !== newState.data.submission.build.passed) {
        const buildPassed = newState.data.submission.build.passed;
        enqueueSnackbar(
          `Build ${buildPassed ? 'passed' : 'failed'}`,
          {variant: (buildPassed ? 'success' : 'error')});
      }
      for (let index = 0; index < oldState.data.submission.tests.length; index++) {
        const oldTest = oldState.data.submission.tests[index];
        const newTest = newState.data.submission.tests[index];

        if (oldTest.result.passed !== newTest.result.passed) {
          enqueueSnackbar(
            `${newTest.test.name} ${newTest.result.passed ? 'passed' : 'failed'}`,
            {variant: (newTest.result.passed ? 'success' : 'error')});
        }
      }
    });

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;


  function translateSubmission({created, ...other}) {
    return {
      date_submitted: created.split(' ')[1], timestamp: new Date(created), time_submitted: created.split(' ')[0],
      ...other,
    };
  }

  const submission = translateSubmission(data.submission);
  const onTime = submission.timestamp <= new Date(submission.assignment_due);
  const {build, tests} = submission;

  return (
    <Grid
      container
      direction="row"
      justify="center"
      alignItems="center"
      spacing={6}
    >

      {/* Upper description */}
      <Grid item xs={12} key={'description'}>
        <Typography variant="h6">
          Submission
        </Typography>
        <Typography variant="body1" className={classes.subtitle}>
          {submission.course_code}
        </Typography>
        <Typography variant="body1" className={classes.subtitle}>
          {submission.commit}
        </Typography>
      </Grid>

      {/* Summary */}
      <Grid item xs={12} key={'summary'}>
        <SubmissionSummary
          submission={submission}
          onTime={onTime}
          regrade={regrade}
          enqueueSnackbar={enqueueSnackbar}
        />
      </Grid>

      {/* Build */}
      <Grid item xs={12} key={'build'}>
        <SubmissionBuild build={build}/>
      </Grid>

      {/* Tests */}
      <Grid item xs={12} key={'tests'}>
        <SubmissionTests tests={tests}/>
      </Grid>

    </Grid>
  );
}
