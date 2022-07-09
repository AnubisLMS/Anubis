import React from 'react';
import {Link} from 'react-router-dom';

import makeStyles from '@mui/styles/makeStyles';
import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

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
