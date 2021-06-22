import React from 'react';
import useSWR from 'swr';
import {Redirect} from 'react-router-dom';

import CircularProgress from '@material-ui/core/CircularProgress';
import Zoom from '@material-ui/core/Zoom';
import Typography from '@material-ui/core/Typography';

import QuestionGrid from './QuestionGrid';

export default function Questions({assignment_id}) {
  const {isValidating: loading, error, data} = useSWR(`/api/public/questions/get/${assignment_id}`);

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
        <QuestionGrid questions={data.questions}/>
      </React.Fragment>
    </Zoom>
  );
}
