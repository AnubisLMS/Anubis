import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import useQuery from '../../hooks/useQuery';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import StudentCard from '../../Components/Admin/Stats/Submissions/StudentCard';
import SubmissionSummary from '../../Components/Public/Submission/SubmissionSummary';
import SubmissionBuild from '../../Components/Public/Submission/SubmissionBuild';
import SubmissionTests from '../../Components/Public/Submission/SubmissionTests';
import QuestionsCard from '../../Components/Public/Questions/QuestionsCard';

import {translateSubmission} from '../../Utils/submission';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

export default function SubmissionStats() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [student, setStudent] = useState(null);
  const [course, setCourse] = useState(null);
  const [assignment, setAssignment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [submission, setSubmission] = useState(null);

  React.useEffect(() => {
    axios.get(`/api/admin/stats/submission/${query.get('submissionId')}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setStudent(data.student);
        setCourse(data.course);
        setAssignment(data.assignment);
        setQuestions(data.questions);
        setSubmission(translateSubmission(data.submission));
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
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <StudentCard student={student}/>
            </Grid>
            <Grid item xs={12}>
              <QuestionsCard questions={questions}/>
            </Grid>
            <Grid item xs={12} md={4}>
              <SubmissionSummary submission={submission} regrade={() => null}/>
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
