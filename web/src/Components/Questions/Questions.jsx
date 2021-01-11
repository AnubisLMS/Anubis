import useQuery from '../../hooks/useQuery';
import useGet from '../../hooks/useGet';
import React from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import {Redirect} from 'react-router-dom';
import Zoom from '@material-ui/core/Zoom';
import Typography from '@material-ui/core/Typography';
import QuestionGrid from './QuestionGrid';

export default function Questions() {
  const query = useQuery();
  const assignmentId = query.get('assignmentId');
  const {loading, error, data} = useGet(`/api/public/assignment/questions/get/${assignmentId}`);

  if (assignmentId === null) return <React.Fragment/>;
  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  function translateQuestion({response, question}) {
    return {
      question: question.question, codeQuestion: question.code_question, codeLanguage: question.code_language,
      sequence: question.sequence, response: response,
    };
  }

  const questions = data.questions.map(translateQuestion);

  if (questions.length === 0) {
    return <React.Fragment/>;
  }

  return (
    <Zoom in={true} timeout={200}>
      <React.Fragment>
        <Typography variant="body1">
          Questions
        </Typography>
        <QuestionGrid questions={questions}/>
      </React.Fragment>
    </Zoom>
  );
}
