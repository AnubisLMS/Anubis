import React, {useState} from 'react';

import makeStyles from '@mui/styles/makeStyles';
import green from '@mui/material/colors/green';
import {Tooltip} from '@mui/material';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';

import {useHistory} from 'react-router-dom';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import clsx from 'clsx';

import SubmissionTestExpanded from '../SubmissionTestExpanded/SubmissionTestExpanded';
import SubmissionContent from '../SubmissionContent/SubmissionContent';
import SubmissionTest from '../SubmissionTest/SubmissionTest';
import SubmissionHeader from '../SubmissionHeader/SubmissionHeader';
import {submissionUpdateSubscribe} from '../../../constant';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {translateSubmission} from '../../../utils/submission';
import standardErrorHandler from '../../../utils/standardErrorHandler';


const useStyles = makeStyles((theme) => ({
  heading: {
    padding: theme.spacing(2),
    alignItems: 'center',
    display: 'flex',
  },
  hiddenIcon: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
  fabProgress: {
    color: green[500],
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
  submissionContentContainer: {
    width: '100%',
    marginTop: theme.spacing(2),
  },
}));

const regrade = (
  {submission, setSubmission, setStep, setErrorStop},
  continueSubscribe,
  enqueueSnackbar,
) => () => {
  if (!submission.processed) {
    return enqueueSnackbar('Submission must first finish tests before regrading.', {variant: 'warning'});
  }

  axios
    .get(`/api/public/submissions/regrade/${submission.commit}`)
    .then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setErrorStop(false);
        setStep(-1);
        setSubmission(null);
        continueSubscribe();
        enqueueSnackbar('Regrading submission', {variant: 'success'});
      } else {
        enqueueSnackbar(`Unable to regrade`, {variant: 'error'});
      }
    })
    .catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
};


export default function SubmissionTests({submissionId}) {
  const classes = useStyles();
  const [step, setStep] = useState(0);
  const [modalTest, setModalTest] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [submission, setSubmission] = useState(null);
  const {enqueueSnackbar} = useSnackbar();
  const history = useHistory();

  const continueSubscribe = () => setTimeout(() => {
    if (step < submissionUpdateSubscribe) {
      setStep((state) => ++state);
    }
  }, 1000);

  React.useEffect(() => {
    if (!submissionId) {
      return;
    }
    axios.get(
      `/api/public/submissions/get/${submissionId}`,
    ).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (!data) {
        return;
      }

      const newSubmission = translateSubmission(data.submission);

      // sort all the tests in Alpha Order
      newSubmission.tests.sort(function(a, b) {
        return a.test.order > b.test.order;
      });

      setSubmission(newSubmission);


      if (!submission) {
        return continueSubscribe();
      }

      if (submission.build.passed !== newSubmission.build.passed) {
        if (newSubmission.build.passed === true) {
          enqueueSnackbar('Build passed', {variant: 'success'});
        } else if (newSubmission.build.passed === false) {
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
  }, [step, submissionId]);

  const expandModal = (test) => {
    setModalTest(test);
    setIsExpanded(true);
  };

  const closeModal = () => {
    setIsExpanded(false);
    setModalTest(null);
  };

  if (!submissionId || !submission) {
    return null;
  }

  const pipelineLogTest = {
    test: {
      name: 'Pipeline Log',
    },
    result: {
      test_name: 'Pipeline Log',
      passed: !!submission?.build?.passed,
      message: 'Not Visible to Students',
      output_type: 'text',
      output: submission?.pipeline_log ?? null,
    },
  };

  const buildTest = {
    test: {
      name: 'Build',
    },
    result: {
      test_name: 'Build',
      passed: !!submission?.build?.passed,
      message: !!submission?.build?.passed ? 'Build Succeeded' : 'Build Failed',
      output_type: 'text',
      output: submission?.build?.stdout ?? null,
    },
  };


  return (
    <React.Fragment>
      {!!submission?.pipeline_log && (
        <Box sx={{m: 1}}>
          <Tooltip title="Delete submission forever from Anubis">
            <Button
              variant={'contained'}
              color={'error'}
              startIcon={<DeleteForeverIcon/>}
              className={clsx(classes.dataItem)}
              onClick={() => {
                axios.delete(`/api/admin/submissions/delete/${submissionId}`).then((response) => {
                  const data = standardStatusHandler(response, enqueueSnackbar);
                  if (data) {
                    history.go(-1);
                  }
                }).catch(standardErrorHandler(enqueueSnackbar));
              }}
            >
              Delete
            </Button>
          </Tooltip>
        </Box>
      )}
      <Box className={classes.headerContainer}>
        <SubmissionHeader
          admin={!!submission?.pipeline_log}
          regrade={regrade(
            {submission, setSubmission, setStep},
            continueSubscribe,
            enqueueSnackbar,
          )}
          {...submission}
        />
      </Box>
      <Box className={classes.submissionContentContainer}>
        <SubmissionContent submission={submission}>
          {submission?.pipeline_log && (
            <SubmissionTest
              test={pipelineLogTest}
              processing={submission.processing}
              expandModal={() => expandModal(pipelineLogTest)}
            />
          )}
          {!submission.commit.startsWith('fake-') && (
            <SubmissionTest
              test={buildTest}
              processing={submission.processing}
              expandModal={() => expandModal(buildTest)}
            />
          )}
          {submission?.tests && submission.tests.map((test, index) => (
            <SubmissionTest
              key={index}
              test={test}
              processing={submission.processing}
              expandModal={() => expandModal(test)}
            />
          ))}
        </SubmissionContent>
      </Box>
      {modalTest &&
        <SubmissionTestExpanded
          open={isExpanded}
          submissionID={submission.commit}
          assignmentName={submission.assignment_name}
          testName={modalTest.result.test_name}
          testSuccess={modalTest.result.passed}
          testOutputType={modalTest.result.output_type}
          testOutput={modalTest.result.output}
          testMessage={modalTest.result.message}
          onClose={() => closeModal()}
        />
      }
    </React.Fragment>
  );
}
