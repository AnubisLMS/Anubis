import React, {Fragment, useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import clsx from 'clsx';
import gfm from 'remark-gfm';
import ReactMarkdownWithHtml from 'react-markdown/with-html';

import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';

import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined';
import LaunchIcon from '@mui/icons-material/Launch';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

import {useStyles} from './Assignment.styles';
import {translateSubmission} from '../../../../utils/submission';
import SubmissionItem from '../../../../components/core/SubmissionItem/SubmissionItem';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import useQuery from '../../../../hooks/useQuery';
import IDEDialog from '../../../../components/core/IDE/IDEDialog';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import Questions from '../../../../components/core/Questions/Questions';


const Assignment = () => {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [selectedTheia, setSelectedTheia] = useState(null);

  const [runAssignmentPolling, setRunAssignmentPolling] = useState(false);

  const assignmentId = query.get('assignmentId');
  const courseId = query.get('courseId');
  const userId = query.get('userId');

  useEffect(() => {
    axios.get(`/api/public/submissions/`, {
      params: {
        assignmentId, courseId, userId,
      },
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setSubmissions(data.submissions.map(translateSubmission));
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    axios.get(`/api/public/assignments/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignment(data.assignment);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (runAssignmentPolling) {
      const endPollingTimeout = setTimeout(() => {
        setRunAssignmentPolling(false);
      }, 60_0000);

      const runPollingInterval = setInterval(() => {
        axios.get(`/api/public/repos/get/${assignmentId}`)
          .then((response) => {
            const data = standardStatusHandler(response, enqueueSnackbar);
            setRunAssignmentPolling(false);
            setAssignment(data.assignment);
          }).catch(standardErrorHandler(enqueueSnackbar));
      }, 1_000);

      return () => {
        clearTimeout(endPollingTimeout);
        clearInterval(runPollingInterval);
      };
    }
    ;
  }, [runAssignmentPolling]);


  const createAssignmentRepo = () => {
    axios.post(`/api/public/repos/create/${assignmentId}`)
      .then((response) => {
        standardStatusHandler(response, enqueueSnackbar);
        setRunAssignmentPolling(true);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <StandardLayout>
      <IDEDialog selectedTheia={selectedTheia} setSelectedTheia={setSelectedTheia}/>
      {assignment && (
        <Box className={classes.root}>
          <Box position="sticky" top={42} className={classes.header}>
            <Box className={classes.headerLeft}>
              <Box className={classes.iconOuterCircle}>
                <Box className={classes.iconInnerCircle}>
                  <AssignmentOutlinedIcon/>
                </Box>
              </Box>
              <Box className={classes.headerText}>
                <Typography className={classes.headerAssignmentName}>
                  {assignment.name}
                </Typography>
                <Typography className={classes.headerCourseName}>
                  from{' '}
                  <a
                    className={classes.headerCourseLink}
                    href={`/course?courseId=${assignment.course.id}`}
                  >
                    {assignment.course.name}
                  </a>
                </Typography>
              </Box>
            </Box>
            <Box className={classes.headerRight}>
              <Button
                color={'primary'}
                variant={'contained'}
                className={classes.ideButton}
                onClick={() => setSelectedTheia(assignment)}
                disabled={assignment.github_repo_required && !assignment.has_repo}
              >
                <LaunchIcon className={classes.launchIcon}/>
                Open Anubis Cloud IDE
              </Button>
              {assignment.github_repo_required && (
                <Fragment>
                  {
                    assignment.has_repo ? (
                      <Button
                        color={'primary'}
                        variant={'contained'}
                        className={classes.repoButton}
                        href={assignment.repo_url}
                        component="a"
                        rel="noopener noreferrer"
                        target="_blank"
                      >
                      View Repo
                      </Button>
                    ) : (
                      <Button onClick={createAssignmentRepo} className={classes.repoButton}>
                        {runAssignmentPolling ? (
                          <CircularProgress size={24}/>
                        ) : 'Create Repo'}
                      </Button>
                    )
                  }
                </Fragment>
              )}
            </Box>
          </Box>
          <Divider/>
          <Box className={classes.content}>
            <Typography className={classes.sectionHeader}>
              Overview
            </Typography>
            <Box className={classes.overviewContent}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Box className={classes.overviewItem}>
                    <Typography className={classes.overviewItemTitle}>ASSIGNMENT DUE DATE</Typography>
                    <Typography className={classes.overviewItemSubtitle}>{assignment.due_date}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  {assignment.shell_autograde_enabled ? (
                    <Box className={
                      clsx(classes.overviewItem, !assignment.has_submission ? classes.colorRed : (
                        assignment.complete ? classes.colorGreen : classes.colorOrange
                      ))
                    }>
                      <Typography className={classes.overviewItemTitle}>SUBMITTED</Typography>
                      <Box className={classes.overviewItemSubtitle}>
                        {assignment.complete ? <CheckCircleIcon/> : <CancelIcon/>}
                        <Typography className={classes.overviewItemSubtitleText}>
                          <Fragment>
                            {assignment.complete ? 'Complete' : 'Incomplete'}
                          </Fragment>
                        </Typography>
                      </Box>
                    </Box>
                  ) : (
                    <Box className={
                      clsx(classes.overviewItem, assignment.has_submission ? classes.colorGreen : classes.colorRed)
                    }>
                      <Typography className={classes.overviewItemTitle}>SUBMITTED</Typography>
                      <Box className={classes.overviewItemSubtitle}>
                        {!assignment.has_submission ? <CancelIcon/> : <CheckCircleIcon/>}
                        <Typography className={classes.overviewItemSubtitleText}>
                          <Fragment>
                            {!assignment.has_submission ? 'No Submission' : 'Sucessfully Submitted'}
                          </Fragment>
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box className={
                    clsx(classes.overviewItem, assignment.has_repo ? classes.colorGreen : classes.colorRed)
                  }>
                    <Typography className={classes.overviewItemTitle}>GITHUB REPOSITORY</Typography>
                    <Box className={classes.overviewItemSubtitle}>
                      {!assignment.has_repo ? <CancelIcon/> : <CheckCircleIcon/>}
                      <Typography className={classes.overviewItemSubtitleText}>
                        {!assignment.has_repo ? 'No Repository' : 'Repository Created'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
              <br/>
              <Divider/>
              <br/>
              <Box className={classes.overviewItem}>
                <Typography className={classes.overviewItemTitle}>DESCRIPTION</Typography>
                <ReactMarkdownWithHtml
                  className={classes.markdown}
                  remarkPlugins={[gfm]}
                  allowDangerousHtml
                >
                  {assignment.description ?? ''}
                </ReactMarkdownWithHtml>
              </Box>
            </Box>
            <br/>
            <br/>
            <Typography className={classes.sectionHeader}>
              Questions
            </Typography>
            <Box className={classes.questionContent}>
              <Questions classes={classes} assignment_id={assignmentId}/>
            </Box>
            <br/>
            <br/>
            <Typography className={classes.sectionHeader}>
              Submissions
            </Typography>
            <Box className={classes.questionContent}>
              {submissions.length === 0 &&
                <Box className={classes.emptyQuestions}>
                  <Typography className={classes.emptyQuestionsText}>
                    Oh no! There are no submissions yet.
                  </Typography>
                </Box>
              }
              {submissions && submissions.map((submission, index) => (
                <SubmissionItem
                  key={`${submission.submission_name}-${index}`}
                  assignmentDue={submission.assignment_due}
                  assignmentName={submission.assignment_name}
                  id={submission.id}
                  commit={submission.commit}
                  processed={submission.processed}
                  tests={submission.tests}
                  timeStamp={submission.last_updated}
                />

              ))}
            </Box>
          </Box>
        </Box>
      )}
    </StandardLayout>
  );
};

export default Assignment;
