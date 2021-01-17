import React, {useState} from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import green from '@material-ui/core/colors/green';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import useQuery from '../../hooks/useQuery';
import SubmissionSummary from '../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../Components/Public/Submission/SubmissionBuild';
import SubmissionTests from '../../Components/Public/Submission/SubmissionTests';
import standardStatusHandler from '../../Utils/standardStatusHandler';

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

const regrade = ({commit, submission, setSubmission, setStep, setErrorStop}, enqueueSnackbar) => () => {
  if (!submission.processed) {
    return enqueueSnackbar('Submission must first finish tests before regrading.', {variant: 'warning'});
  }

  axios
    .get(`/api/public/regrade/${commit}`)
    .then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setErrorStop(false);
        setStep(-1);
        setSubmission(null);
        enqueueSnackbar('Regrading submission', {variant: 'success'});
      } else {
        enqueueSnackbar(`Unable to regrade`, {variant: 'error'});
      }
    })
    .catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
};

const translateSubmission = ({created, assignment_due, ...other}) => ({
  date_submitted: created.split(' ')[1], timestamp: new Date(created), time_submitted: created.split(' ')[0],
  assignment_due, on_time: new Date(created) <= new Date(assignment_due), created, ...other,
});


export default function Submission() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [step, setStep] = useState(0);
  const [submission, setSubmission] = useState(null);
  const [errorStop, setErrorStop] = useState(false);

  const continueSubscribe = () => setTimeout(() => {
    if (step < 60) {
      setStep((state) => ++state);
    }
  }, 1000);

  React.useEffect(() => {
    axios.get(
      `/api/public/submissions/get/${query.get('commit')}`,
    ).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (!data) {
        return;
      }

      const newSubmission = translateSubmission(data.submission);
      setSubmission(newSubmission);

      if (!submission) {
        return continueSubscribe();
      }

      if (submission.build.passed !== newSubmission.build.passed) {
        if (newSubmission.build.passed) {
          enqueueSnackbar('Build passed', {variant: 'success'});
        } else {
          setErrorStop(true);
          return enqueueSnackbar('Build failed', {variant: 'error'});
        }
      }

      for (let index = 0; index < submission.tests.length; index++) {
        const oldTest = submission.tests[index];
        const newTest = newSubmission.tests[index];

        if (oldTest.result.passed !== newTest.result.passed) {
          enqueueSnackbar(
            `${newTest.test.name} ${newTest.result.passed ? 'passed' : 'failed'}`,
            {variant: (newTest.result.passed ? 'success' : 'error')});
        }
      }

      continueSubscribe();
    }).catch((error) => enqueueSnackbar(error.toString(), {variant: 'error'}));
  }, [step]);

  if (!submission) {
    return null;
  }

  const {build, tests} = submission;
  const pageState = {
    commit: query.get('commit'),
    step, setStep,
    submission, setSubmission,
    errorStop, setErrorStop,
  };

  return (
    <Grid
      container
      justify="center"
      alignItems="flex-start"
      direction={'row'}
      spacing={2}
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
      <Grid item xs={12} md={4} key={'summary'}>
        <SubmissionSummary
          submission={submission}
          onTime={submission.on_time}
          regrade={regrade(pageState, enqueueSnackbar)}
          enqueueSnackbar={enqueueSnackbar}
          stop={errorStop}
        />
      </Grid>

      <Grid item xs={12} md={8} key={'build-test'}>
        <Grid container spacing={1}>
          {/* Build */}
          <Grid item xs={12} key={'build'}>
            <SubmissionBuild build={build} stop={errorStop}/>
          </Grid>

          {/* Tests */}
          <Grid item xs={12} key={'tests'}>
            <SubmissionTests tests={tests} stop={errorStop}/>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
}
