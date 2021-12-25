import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import {translateSubmission} from '../../../Utils/submission';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';

import useQuery from '../../../Hooks/useQuery';

import StudentCard from '../../../Components/Admin/Stats/Submissions/StudentCard';
import SubmissionSummary from '../../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../../Components/Public/Submission/SubmissionBuild';
import SubmissionTests from '../../../Components/Public/Submission/SubmissionTests';
import QuestionsCard from '../../../Components/Public/Questions/QuestionsCard';
import StudentGitCard from '../../../Components/Admin/Stats/Submissions/StudentGitCard';
import StudentAssignmentHistory from '../../../Components/Admin/Visuals/StudentAssignmentHistory';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

export default function Submission() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [student, setStudent] = useState(null);
  const [course, setCourse] = useState(null);
  const [assignment, setAssignment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [submission, setSubmission] = useState(null);

  const assignmentId = query.get('assignmentId');
  const netid = query.get('netid');

  React.useEffect(() => {
    axios.get(`/api/admin/autograde/submission/${assignmentId}/${netid}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setStudent(data.student);
        setCourse(data.course);
        setAssignment(data.assignment);
        setQuestions(data.questions);
        setSubmission(data.submission ? translateSubmission(data.submission) : 'No submission');
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justify={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Submission Autograde Result
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Results for {assignment?.name}
          </Typography>
        </Grid>
        <Grid item xs={12} md={10}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <StudentAssignmentHistory/>
            </Grid>
            <Grid item xs>
              <StudentCard student={student}/>
            </Grid>
            <Grid item xs>
              <StudentGitCard submission={submission}/>
            </Grid>
            <Grid item xs={12}>
              <QuestionsCard questions={questions}/>
            </Grid>
            <Grid item xs={12} md={4}>
              <SubmissionSummary submission={submission} regrade={null}/>
            </Grid>
            <Grid item xs={12} md={4}>
              <SubmissionBuild build={submission?.build}/>
            </Grid>
            <Grid item xs={12} md={4}>
              <SubmissionTests tests={submission?.tests}/>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
