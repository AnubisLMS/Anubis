import React from 'react';
import {Link} from 'react-router-dom';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 500,
  },
  textField: {
    margin: theme.spacing(1),
  },
}));


export default function CourseCard({user, course}) {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardContent>
          {/* Course Code */}
          <Typography gutterBottom variant="subtitle1">
            {course.course_code}
          </Typography>

          {/* Course Name */}
          <Typography gutterBottom variant="body2">
            {course.name}
          </Typography>

          {/* Course Section */}
          <Typography gutterBottom variant="body2">
            Section {course.section}
          </Typography>

          {/* Course Professor */}
          <Typography gutterBottom variant="body2">
            Professor {course.professor}
          </Typography>

          {/* Course Professor */}
          <Typography gutterBottom variant="body2">
            Total visible assignments {course.total_assignments}
          </Typography>


        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button
          variant="contained"
          color="primary"
          size="small"
          component={Link}
          to={`/courses/assignments/submissions?courseId=${course.id}&userId=${user.id}`}
        >
          View Submissions
        </Button>
      </CardActions>
    </Card>
  );
}
