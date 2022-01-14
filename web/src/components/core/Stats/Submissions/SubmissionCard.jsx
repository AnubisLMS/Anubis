import React from 'react';
import {Link} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
  root: {
    minWidth: 275,
  },
});


export default function SubmissionCard({submission}) {
  const classes = useStyles();

  if (!submission) {
    return null;
  }

  return (
    <Card className={classes.root}>
      <CardContent>
        <Typography variant={'h6'}>
          Submission
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Commit: {submission.commit.substr(0, 6)}
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          State: {submission.state}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          component={Link}
          to={`/submission?commit=${submission.commit}`}
        >
          View Submission
        </Button>
      </CardActions>
    </Card>
  );
}
