import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import {useStyles} from './Submission.styles';
import useQuery from '../../../hooks/useQuery';
import {translateSubmission} from '../../../Utils/submission';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import SubmissionSummary from '../../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../../Components/Public/Submission/SubmissionBuild';
import SubmissionContent from '../../../Components/Public/Submission/SubmissionContent/SubmissionContent';
import SubmissionTest from '../../../Components/Public/Submission/SubmissionTest/SubmissionTest';
import SubmissionTests from '../../../Components/Public/Submission/SubmissionTests';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [curtest, setCurtest] = useState();
  const handleOpen = (test) => {
    setCurtest(test);
    setIsModalOpen(!isModalOpen);
  };
  const handleClose = () => (
    setIsModalOpen(!isModalOpen)
  );

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
    <StandardLayout title={'Anubis Submission'} description={[
      `Assignment: ${submission.assignment_name}`,
      submission.commit,
    ]}>
      <Grid container spacing={4}>

        <Grid item xs={12} md={12} key={'build-test'}>
          {/* Build */}
          <SubmissionContent submission={submission}>
            {tests.map((test)=>(
              <Box key={test.test.id}>
                <SubmissionTest test={test} callback={handleOpen}/>
              </Box>
            ))}
          </SubmissionContent>
        </Grid>
        <Grid container justifyContent="center">
          <SubmissionTestExpanded
            showModal={isModalOpen}
            handleClose={handleClose}
            assignmentName={submission.assignment_name}
            testName={curtest==null?'':curtest.test.name}
          />
        </Grid>
      </Grid>
    </StandardLayout>
  );
}

