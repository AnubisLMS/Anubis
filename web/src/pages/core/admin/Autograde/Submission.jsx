import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

import {translateSubmission} from '../../../../utils/submission';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

import useQuery from '../../../../hooks/useQuery';

import StudentCard from '../../../../components/core/Stats/Submissions/StudentCard';
import SubmissionSummary from '../../../../components/core/Submission/SubmissionSummary';
import SubmissionBuild from '../../../../components/core/Submission/SubmissionBuild';
import SubmissionTests from '../../../../components/core/Submission/SubmissionTests';
import QuestionsCard from '../../../../components/core/Questions/QuestionsCard';
import StudentGitCard from '../../../../components/core/Stats/Submissions/StudentGitCard';
import StudentAssignmentHistory from '../../../../components/core/Visuals/StudentAssignmentHistory';


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
      <Grid container spacing={4} justifyContent={'center'}>
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
              <StudentCard student={student} assignment={assignment}/>
            </Grid>
            <Grid item xs>
              <StudentGitCard submission={submission}/>
            </Grid>
            <Grid item xs={12}>
              <QuestionsCard questions={questions}/>
            </Grid>
            <Grid item xs={12}>
              <SubmissionTests submissionId={submission?.id}/>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
