import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import clsx from 'clsx';

import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import {useStyles} from './Submission.styles';
import useQuery from '../../../hooks/useQuery';
import {translateSubmission} from '../../../Utils/submission';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import SubmissionContent from '../../../Components/Public/Submission/SubmissionContent/SubmissionContent';
import SubmissionHeader from '../../../Components/Public/Submission/SubmissionHeader/SubmissionHeader';
import SubmissionTest from '../../../Components/Public/Submission/SubmissionTest/SubmissionTest';
import SubmissionTestExpanded
  from '../../../Components/Public/Submission/SubmissionTestExpanded/SubmissionTestExpanded';

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
  const [modalTest, setModalTest] = useState(undefined);
  const [isExpanded, setIsExpanded] = useState(false);

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
  }, []);
  console.log(submission);

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

  const expandModal = (test) => {
    setModalTest(test);
    setIsExpanded(true);
  };

  const closeModal = () => {
    setIsExpanded(false);
  };

  return (
    <StandardLayout title={'Anubis Submission'} description={[
      `Assignment: ${submission.assignment_name}`,
      submission.commit,
    ]}>
      {modalTest && isExpanded &&
        <Box className={classes.backDrop} />
      }
      <Grid container className={classes.root}>
        <Box className={
          modalTest && isExpanded ?
            clsx(classes.headerContainer, classes.blur) :
            classes.headerContainer}>
          <SubmissionHeader {...submission} />
        </Box>
        <Box className={
          modalTest && isExpanded ?
            clsx(classes.submissionContentContainer, classes.blur) :
            classes.submissionContentContainer}>
          <SubmissionContent submission={submission}>
            <SubmissionTest test= {{
              test: {
                name: 'Build',
              },
              result: {
                passed: submission.build.passed,
              },
            }} />
            {submission?.tests && submission.tests.map((test, index) => (
              <SubmissionTest key={index} test={test} expandModal = {() => expandModal(test)}/>
            ))}
          </SubmissionContent>

        </Box>
        {modalTest && isExpanded &&
          <Box className={classes.expandedContainer}>
            <SubmissionTestExpanded
              testName={modalTest.result.test_name}
              submissionID={submission.commit}
              assignmentName={submission.assignment_name}
              testSuccess={modalTest.result.passed}
              onClose={() => closeModal()}
            />
          </Box>
        }
      </Grid>
    </StandardLayout>
  );
}

