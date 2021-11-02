import Grid from '@material-ui/core/Grid';
import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import QuestionsCard from './QuestionsCard';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
  },
  card: {
    minWidth: '512',
  },
}));

export default function QuestionGrid({questions}) {
  const classes = useStyles();

  return (
    <Grid
      container
      spacing={4}
      className={classes.root}
    >
      <Grid item xs={12}>
        <QuestionsCard questions={questions}/>
      </Grid>
    </Grid>
  );
}
