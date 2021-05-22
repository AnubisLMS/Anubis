import React from 'react';
import {Redirect} from 'react-router-dom';

import CircularProgress from '@material-ui/core/CircularProgress';
import Zoom from '@material-ui/core/Zoom';
import Typography from '@material-ui/core/Typography';

import QuestionGrid from './QuestionGrid';
import useGet from '../../../hooks/useGet';

export default function Questions({assignment_id}) {
  const [{loading, error, data}] = useGet(`/api/public/questions/get/${assignment_id}`);

  if (assignment_id === null) return <React.Fragment/>;
  if (loading) return <CircularProgress/>;
  if (error) return <Redirect to={`/error`}/>;

  if (data.questions.length === 0) {
    return <React.Fragment/>;
  }

  return (
    <Zoom in={true} timeout={200}>
      <React.Fragment>
        <Typography variant="body1">
          Questions
        </Typography>
        <QuestionGrid questions={data.questions.sort(({question: q1}, {question: q2}) => q1.pool - q2.pool)}/>
      </React.Fragment>
    </Zoom>
  );
}
