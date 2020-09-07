import React, {useState} from "react";
import {makeStyles, useTheme} from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import AlarmIcon from '@material-ui/icons/Alarm';
import EventNoteIcon from '@material-ui/icons/EventNote';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import {Link} from "react-router-dom";
import red from '@material-ui/core/colors/red';
import PublishIcon from '@material-ui/icons/Publish';
import green from '@material-ui/core/colors/green';
import blue from '@material-ui/core/colors/blue';
import grey from '@material-ui/core/colors/grey'

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    minWidth: 210
  },
  pos: {
    marginBottom: 5
  },
  title: {
    fontSize: 13
  },
  datePos: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 0
  },
  dateText: {
    fontSize: 15,
    marginTop: 20,

  },
  statusPos: {
    display: 'flex',

  },
  statusText: {
    fontSize: 14,
    marginTop: 5,

  },
  datetext: {
    fontSize: 14,
    paddingLeft: theme.spacing(1)
  },
  submitIcon: {
    display: 'flex',
    paddingLeft: theme.spacing(0.5),

  },
  mainTitle: {
    fontWeight: 600,
    fontSize: 20,
    letterspacing: 0.4,

  },
}));


const remainingTime = (dueDate) => {
  const difference = +new Date(dueDate) - +new Date();
  let timeLeft = {};
  if (difference > 0) {
    timeLeft = {
      days: Math.floor(difference / (1000 * 60 * 60 * 24)),
      hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
      mins: Math.floor((difference / 1000 / 60) % 60),
    };
  }
  return timeLeft;
}

export default function AssignmentCard(props) {
  const {courseCode, assignmentId, assignmentNumber, assignmentTitle, dueDate, hasSubmission} = props.assignment;
  const classes = useStyles();

  const [timeLeft, setTimeLeft] = useState(remainingTime(dueDate));
  const timerComponents = [];
  const theme = useTheme();
  Object.keys(timeLeft).forEach((interval) => {
    if (!timeLeft[interval]) {
      return;
    }
    timerComponents.push( //decorate
      <span>

          {timeLeft[interval]} {interval} left
        </span>
    );
  });


  return (
    <Card className={classes.root}>
      <CardActionArea
        component={Link}
        // to={`/courses/${courseCode.replace(/\s+/g, '')}/assignments/${assignmentNumber}/info`}>
        to={`/courses/assignments/submissions`}>
        <CardContent>

          <Typography className={classes.title} color="textSecondary" gutterBottom>
            {courseCode}
          </Typography>

          <Typography className={classes.mainTitle}>
            {assignmentTitle}
          </Typography>

          <Typography className={classes.pos} color="textSecondary">
            {`Assignment ${assignmentNumber}`}
          </Typography>

          <div className={classes.datePos}>
            <EventNoteIcon style={{marginRight: 7}}/>
            <p className={classes.dateText}> {` Due: ${(new Date(dueDate)).toLocaleDateString()}`} </p>
          </div>

          <div className={classes.statusPos} style={hasSubmission ? {} : {color: red[500]}}>
            {hasSubmission ?
              <CheckCircleIcon style={{color: green[500], marginRight: 6}}/> :
              <AlarmIcon style={{marginRight: 7}}/>
            }

            <p className={classes.statusText}>
              {hasSubmission ?
                "Assignment Submitted" :
                timerComponents.length ?
                  timerComponents[0] :
                  "Past Due"}
            </p>
          </div>

        </CardContent>
      </CardActionArea>
      <CardActions>
        <div className={classes.submitIcon}>
          <PublishIcon style={hasSubmission ? {color: blue[500]} : {color: grey[500]}}/>
          <Button
            component={Link}
            to={`/courses/assignments/submissions?assignment=${assignmentTitle}`}
            style={hasSubmission ? {color: blue[500]} : {color: grey[500]}} size="small"
            disabled = {!hasSubmission}>
            Submissions</Button>

        </div>
      </CardActions>
    </Card>
  );
}