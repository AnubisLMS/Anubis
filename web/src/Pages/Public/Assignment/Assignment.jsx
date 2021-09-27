import React, {useState, useEffect} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import clsx from 'clsx';

import Grid from '@material-ui/core/Grid';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import AssignmentOutlinedIcon from '@material-ui/icons/AssignmentOutlined';
import LaunchIcon from '@material-ui/icons/Launch';
import Button from '@material-ui/core/Button';
import Divider from '@material-ui/core/Divider';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';

import SubmissionRow from '../Submissions/SubmissionRow/SubmissionRow';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import {useStyles} from './Assignment.styles';
import useQuery from '../../../hooks/useQuery';


const Assignment = () => {
  const query = useQuery();
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const [tab, setTab] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);

  const assignmentId = query.get('assignmentId');
  const courseId = query.get('courseId');
  const userId = query.get('userId');

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
  };

  useEffect(() => {
    axios.get(`/api/public/submissions/`, {
      params: {
        assignmentId, courseId, userId,
        limit: pageSize,
        offset: page * pageSize,
      },
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setSubmissions(data.submissions);
    }).catch((error) => {
      console.log(error);
    });
  }, []);

  useEffect(() => {
    axios.get(`/api/public/assignments/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        console.log(data.assignment);
        setAssignment(data.assignment);
      }
    }).catch((error) => console.log(error));
  }, []);

  return (
    <StandardLayout>
      {assignment && (
        <Box className={classes.root}>
          <Box position="sticky" top={52} className={classes.header}>
            <Box className={classes.headerLeft}>
              <Box className={classes.iconOuterCircle}>
                <Box className={classes.iconInnerCircle}>
                  <AssignmentOutlinedIcon />
                </Box>
              </Box>
              <Box className={classes.headerText}>
                <Typography className={classes.headerAssignmentName}>
                  {assignment.name}
                </Typography>
                <Typography className={classes.headerCourseName}>
                  from <a className={classes.headerCourseLink}>{assignment.course.name} </a>
                </Typography>
              </Box>
            </Box>
            <Box className={classes.headerRight}>
              <Button className={classes.ideButton}>
                <LaunchIcon className={classes.launchIcon}/>
                Open Anubis Cloud IDE
              </Button>
              <Button className={classes.repoButton}>
                View Repo
              </Button>
            </Box>
          </Box>
          <Divider />
          <Box className = {classes.content}>
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
                  <Box className={
                    clsx(classes.overviewItem, assignment.has_submission ? classes.colorGreen : classes.colorRed)
                  }>
                    <Typography className={classes.overviewItemTitle}>SUBMITTED</Typography>
                    <Box className={classes.overviewItemSubtitle}>
                      {!assignment.has_submission ? <CancelIcon /> : <CheckCircleIcon />}
                      <Typography className={classes.overviewItemSubtitleText}>
                        {!assignment.has_submission ? 'No Submission' : 'Sucessfully Submitted'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box className={
                    clsx(classes.overviewItem, assignment.has_repo ? classes.colorGreen : classes.colorRed)
                  }>
                    <Typography className={classes.overviewItemTitle}>GITHUB REPOSITORY</Typography>
                    <Box className={classes.overviewItemSubtitle}>
                      {!assignment.has_repo ? <CancelIcon /> : <CheckCircleIcon />}
                      <Typography className={classes.overviewItemSubtitleText}>
                        {!assignment.has_repo ? 'No Repository' : 'Repository Created'}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
              <br />
              <Divider />
              <br />
              <Box className={classes.overviewItem}>
                <Typography className={classes.overviewItemTitle}>DESCRIPTION</Typography>
                <Typography className={classes.overviewItemSubtitle}>
                  {assignment.description}
                </Typography>
              </Box>
            </Box>
            <br />
            <br />
            <Typography className={classes.sectionHeader}>
              Questions
            </Typography>
            <Box className={classes.questionContent}>
              <Box className={classes.emptyQuestions}>
                <Typography className={classes.emptyQuestionsText}>
                  Oh no! There are no questions for this assignment.
                </Typography>
              </Box>
            </Box>
            <br />
            <br />
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
                <SubmissionRow key={`${submission.commit}-${index}`} {...submission} />
              ))}
            </Box>
          </Box>
        </Box>
      )}
    </StandardLayout>
  );
};

export default Assignment;
