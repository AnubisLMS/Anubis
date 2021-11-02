import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Link} from 'react-router-dom';

import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import Badge from '@material-ui/core/Badge';

// course is visually represented by a card

const useStyles = makeStyles({
  root: {
    flexGrow: 1,

    minWidth: 275,
    maxWidth: 280,
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
  },
  sem: {
    fontSize: 14,

  },
  pos: {
    marginBottom: 12,
  },
  title: {
    marginTop: 10,
  },
});


export default function CourseCard({course}) {
  // will have notification to indicate number of open assignment with no submissions
  const classes = useStyles();
  const bull = <span className={classes.bullet}>•</span>;

  const {
    id,
    name,
    course_code,
    section,
    professor_display_name,
    total_assignments,
    open_assignments,
    semester,
  } = course;

  return (
    <Badge badgeContent={open_assignments} color="error" fontSize="medium">

      <Card className={classes.root}>

        <CardActionArea
          component={Link}
          to={`/courses/assignments?courseId=${id}`}>

          <CardContent>
            <Typography className={classes.sem} color="textSecondary" gutterBottom>
              {semester}
            </Typography>
            <Typography className={classes.title} variant="h6" component="h2">
              {name}
            </Typography>
            <Typography className={classes.pos} color="textSecondary">
              {course_code} {bull} {section}
            </Typography>
            <Typography variant="body2" component="p">
              {professor_display_name}
            </Typography>
          </CardContent>

          <CardActions>
            <Button size="small" color="primary">
              {`${total_assignments} Assigments`}
            </Button>
          </CardActions>

        </CardActionArea>

      </Card>
    </Badge>
  );
}
