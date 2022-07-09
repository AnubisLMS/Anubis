import React from 'react';
import {Link} from 'react-router-dom';

import makeStyles from '@mui/material/styles/makeStyles';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

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
