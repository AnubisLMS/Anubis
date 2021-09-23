import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';

import {useStyles} from './Submission.styles';
import useQuery from '../../../hooks/useQuery';
import {translateSubmission} from '../../../Utils/submission';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import SubmissionSummary from '../../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../../Components/Public/Submission/SubmissionBuild';
import SubmissionTests from '../../../Components/Public/Submission/SubmissionTests';
import standardStatusHandler from '../../../Utils/standardStatusHandler';


const regrade = ({commit, submission, setSubmission, setStep, setErrorStop}, enqueueSnackbar) => () => {
  if (!submission.processed) {
    return enqueueSnackbar('Submission must first finish tests before regrading.', {variant: 'warning'});
  }

  axios
    .get(`/api/public/submissions/regrade/${commit}`)
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


export default function Submission() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [step, setStep] = useState(0);
  const [submission, setSubmission] = useState(null);
  const [errorStop, setErrorStop] = useState(false);

  const continueSubscribe = () => setTimeout(() => {
    if (step < 300) {
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

      if (newSubmission.error || newSubmission.build.passed === false) {
        setErrorStop(true);
        return;
      }

      setErrorStop(false);

      if (!submission) {
        return continueSubscribe();
      }

      if (submission.build.passed !== newSubmission.build.passed) {
        if (newSubmission.build.passed === true) {
          enqueueSnackbar('Build passed', {variant: 'success'});
        } else if (newSubmission.build.passed === false) {
          setErrorStop(true);
          return enqueueSnackbar('Build failed', {variant: 'error'});
        }
      }

      for (let index = 0; index < submission.tests.length; index++) {
        const oldTest = submission.tests[index];
        const newTest = newSubmission.tests[index];

        if (oldTest.result.passed === null && newTest.result.passed !== null) {
          enqueueSnackbar(
            `${newTest.test.name} ${newTest.result.passed ? 'passed' : 'failed'}`,
            {variant: (newTest.result.passed ? 'success' : 'error')});
        }
      }

      if (!submission.processed) {
        continueSubscribe();
      }
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
    <StandardLayout title={'Anubis Submission'} description={[
      `Assignment: ${submission.assignment_name}`,
      submission.commit,
    ]}>
      <Grid container spacing={4}>
        {/* Summary */}
        <Grid item xs={12} md={4} key={'summary'}>
          <SubmissionSummary
            submission={submission}
            regrade={regrade(pageState, enqueueSnackbar)}
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
    </StandardLayout>
  );
}

