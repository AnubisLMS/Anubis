import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Redirect} from "react-router-dom";
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from "@material-ui/core/Tooltip";
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import RefreshIcon from "@material-ui/icons/Refresh";
import CircularProgress from "@material-ui/core/CircularProgress";
import Grid from "@material-ui/core/Grid";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";
import green from "@material-ui/core/colors/green";
import CancelIcon from "@material-ui/icons/Cancel";
import AccessTimeIcon from '@material-ui/icons/AccessTime';
import red from "@material-ui/core/colors/red";
import BuildIcon from '@material-ui/icons/Build';
import Fab from '@material-ui/core/Fab';
import AssessmentIcon from '@material-ui/icons/Assessment';
import {useSnackbar} from 'notistack';
import useSubscribe from "../../../useSubscribe";
import {useQuery} from "../../../utils";
import axios from 'axios';

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
  },
  heading: {
    padding: theme.spacing(2),
    display: 'flex',
    // '& > * + *': {
    //   marginLeft: theme.spacing(2),
    // },
    // fontWeight: theme.typography.fontWeightRegular,
    // flexBasis: '33.33%',
    // flexShrink: 0,
  },

  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
  buttonSuccess: {
    backgroundColor: green[500],
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
    .then(response => {
      if (response.data.success)
        window.location.reload()
      else
        enqueueSnackbar(`Unable to regrade`, {variant: "error"})
    })
    .catch(error => {
      enqueueSnackbar(`Unable to regrade`, {variant: "error"})
    })
}


export default function SubmissionInfo() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const {loading, error, data} = useSubscribe(
    `/api/public/submission/${useQuery().get('commit')}`,
    1000,
    data => data.submission.processed,
    (oldState, newState) => {
      if (oldState.data.submission === undefined) return;
      if (oldState.data.submission.build.passed !== newState.data.submission.build.passed) {
        const buildPassed = newState.data.submission.build.passed;
        enqueueSnackbar(
          `Build ${buildPassed ? 'passed' : 'failed'}`,
          {variant: (buildPassed ? 'success' : 'error')});
      }
      for (let index = 0; index < oldState.data.submission.tests.length; index++) {
        let oldTest = oldState.data.submission.tests[index];
        let newTest = newState.data.submission.tests[index];

        if (oldTest.result.passed !== newTest.result.passed) {
          enqueueSnackbar(
            `${newTest.test.name} ${newTest.result.passed ? 'passed' : 'failed'}`,
            {variant: (newTest.result.passed ? 'success' : 'error')});
        }
      }
    })

  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>

  console.log(data)

  function translateSubmission(
    {
      assignment_name, assignment_due, url, commit,
      processed, state, created, last_updated, repo, tests, build, class_code
    }) {
    return {
      assignmentName: assignment_name, assignmentDue: assignment_due, repoURL: url,
      processed: processed, submissionState: state, timeSubmitted: created.split(' ')[0],
      dateSubmitted: created.split(' ')[1], timeStamp: new Date(created), commitHash: commit,
      submissionTests: tests, submissionBuild: build, submittedAt: created, courseCode: class_code
    };
  }

  const submission = translateSubmission(data.submission);
  const {submissionBuild, submissionTests} = submission;
  const onTime = submission.timeStamp <= submission.assignmentDue;

  return (
    <div>
      <Grid container
            direction="row"
            justify="center"
            alignItems="center"
            spacing={6}>

        {/* Upper description */}
        <Grid item xs={12} key={'description'}>
          <Typography variant="h6">
            Submission
          </Typography>
          <Typography variant="body1" className={classes.subtitle}>
            {submission.courseCode}
          </Typography>
          <Typography variant="body1" className={classes.subtitle}>
            {submission.commitHash}
          </Typography>
        </Grid>

        {/* Summary */}
        <Grid item xs={12} key={'summary'}>
          <Card className={classes.root}>
            <CardActionArea>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  {submission.assignmentName}
                </Typography>
                <List>

                  {/* On time*/}
                  <ListItem>
                    <ListItemIcon>
                      <Tooltip title={onTime
                        ? "Submitted On Time"
                        : "Submitted Late"}>
                        <IconButton component="div">
                          {onTime
                            ? <CheckCircleIcon style={{color: green[500]}}/>
                            : <CancelIcon style={{color: red[500]}}/>}
                        </IconButton>
                      </Tooltip>
                    </ListItemIcon>
                    <ListItemText primary={onTime
                      ? "Submitted On Time"
                      : "Submitted Late"}/>
                  </ListItem>

                  {/* Submission time */}
                  <ListItem>
                    <ListItemIcon>
                      <Tooltip title={`Submitted at ${submission.submittedAt}`}>
                        <IconButton component="div">
                          <AccessTimeIcon color={"primary"}/>
                        </IconButton>
                      </Tooltip>
                    </ListItemIcon>
                    <ListItemText primary={submission.submittedAt}/>
                  </ListItem>

                  {/* Submission state */}
                  <ListItem>
                    <ListItemIcon>
                      <Tooltip title={!submission.processed ? submission.submissionState : "regrade"}>
                        <IconButton component="div" onClick={() =>
                          regrade(submission.commitHash, enqueueSnackbar)}>
                          {submission.processed
                            ? <RefreshIcon color={"primary"}/>
                            : <CircularProgress size="1em"/>}
                        </IconButton>
                      </Tooltip>
                    </ListItemIcon>
                    <ListItemText primary={submission.submissionState}/>
                  </ListItem>

                </List>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>

        {/* Build */}
        <Grid item xs={12} key={'build'}>
          <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon/>}
              aria-controls="panel1a-content"
              id="panel1a-header"
            >
              <div className={classes.wrapper}>
                <Fab
                  aria-label="save"
                  color={submissionBuild.passed === false ? "secondary" : "primary"}
                >
                  {submissionBuild.passed === null ? (
                    <BuildIcon/>
                  ) : submissionBuild.passed === true ? (
                    <CheckCircleIcon/>
                  ) : submissionBuild.passed === false ? (
                    <CancelIcon/>
                  ) : null}
                </Fab>
                {submissionBuild.passed === null && <CircularProgress size={68} className={classes.fabProgress}/>}
              </div>

              <Typography className={classes.heading}>Build</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <div>
                {submissionBuild.stdout
                  ? submissionBuild.stdout.trim().split('\n')
                    .map((line, index) => (
                      <Typography
                        variant={"body1"}
                        color={"textSecondary"}
                        width={100}
                        key={`line-${index}`}
                      >
                        {line}
                      </Typography>
                    ))
                  : null}
              </div>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Tests */}
        <Grid item xs={12} key={'tests'}>
          {submissionTests.map((test, index) => (
            <Accordion key={`test-${index}`}>
              {console.log(test)}
              <AccordionSummary
                expandIcon={<ExpandMoreIcon/>}
                aria-controls="panel2a-content"
                id="panel2a-header"
              >
                <div className={classes.wrapper}>
                  <Fab
                    aria-label="save"
                    color={test.result.passed === false ? "secondary" : "primary"}
                  >
                    {test.result.passed === null ? (
                      <AssessmentIcon/>
                    ) : test.result.passed === true ? (
                      <CheckCircleIcon/>
                    ) : test.result.passed === false ? (
                      <CancelIcon/>
                    ) : null}
                  </Fab>
                  {test.result.passed === null && <CircularProgress size={68} className={classes.fabProgress}/>}
                </div>
                <Typography className={classes.heading}>{test.test.name}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <div>
                  <Typography key={'firstline'} variant={'h5'} className={classes.heading}>
                    {test.result.message}
                  </Typography>
                  {test.result.passed !== null && !!test.result.stdout
                    ? test.result.stdout.trim().split('\n')
                      .map((line, index) => (
                        line.trim().length !== 0
                          ? <Typography
                            variant={"body1"}
                            color={"textSecondary"}
                            width={100}
                            key={`line-${index}`}
                          >
                            {line}
                          </Typography>
                          : <br/>
                      ))
                    : null}
                </div>
              </AccordionDetails>
            </Accordion>
          ))}
        </Grid>

      </Grid>
    </div>
  );
}
