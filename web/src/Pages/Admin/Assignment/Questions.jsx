import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useParams} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';

import QuestionCard from '../../../Components/Admin/Assignment/QuestionCard';
import QuestionControls from '../../../Components/Admin/Assignment/QuestionControls';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

export default function AssignmentQuestions() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const {assignmentId} = useParams();
  const [assignmentName, setAssignmentName] = useState('');
  const [questionsAssigned, setQuestionsAssigned] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get(`/api/admin/questions/get/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      setQuestionsAssigned(data.questions_assigned);
      if (data?.questions) {
        setQuestions(data.questions);
      }
      if (data?.assignment_name) {
        setAssignmentName(data.assignment_name);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const reload = () => {
    setReset((prev) => ++prev);
  };

  const updateQuestion = (index) => (question) => {
    setQuestions((prev) => {
      prev[index] = question;
      return [...prev];
    });
  };

  const saveQuestion = (index) => () => {
    const question = questions[index];
    axios.post(`/api/admin/questions/update/${question.id}`, {question}).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const deleteQuestion = (index) => () => {
    const question = questions[index];
    axios.get(`/api/admin/questions/delete/${question.id}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      reload();
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <div className={classes.root}>
      <Grid container spacing={2} justify={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Assignment Question Management
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <QuestionControls
            assignmentName={assignmentName}
            questionsAssigned={questionsAssigned}
            assignmentId={assignmentId}
            reload={reload}
          />
        </Grid>
        {questions.map((question, index) => (
          <Grid item xs={12} key={`question-${index}`}>
            <QuestionCard
              assignmentQuestion={question}
              updateQuestion={updateQuestion(index)}
              saveQuestion={saveQuestion(index)}
              deleteQuestion={deleteQuestion(index)}
              reload={reload}
            />
          </Grid>
        ))}
      </Grid>
    </div>
  );
}
