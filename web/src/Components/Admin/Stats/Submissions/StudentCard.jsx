import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import {Link} from 'react-router-dom';

const useStyles = makeStyles({
  root: {
    minWidth: 275,
  },
});


export default function StudentCard({student}) {
  const classes = useStyles();

  if (!student) {
    return null;
  }

  return (
    <Card className={classes.root}>
      <CardContent>
        <Typography variant={'h6'}>
          Student
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Name: {student.name}
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Netid: {student.netid}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          component={Link}
          to={`/admin/user?userId=${student.id}`}
        >
          View Student
        </Button>
      </CardActions>
    </Card>
  );
}
