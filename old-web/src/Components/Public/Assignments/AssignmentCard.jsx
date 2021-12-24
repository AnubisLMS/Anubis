import React, {useCallback, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {Link} from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

import grey from '@material-ui/core/colors/grey';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import AlarmIcon from '@material-ui/icons/Alarm';
import GitHubIcon from '@material-ui/icons/GitHub';
import red from '@material-ui/core/colors/red';
import green from '@material-ui/core/colors/green';
import Dialog from '@material-ui/core/Dialog';
import Tooltip from '@material-ui/core/Tooltip';
import Box from '@material-ui/core/Box';

import EventNoteIcon from '@material-ui/icons/EventNote';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import DescriptionIcon from '@material-ui/icons/Description';
import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';

import {nonStupidDatetimeFormat} from '../../../Utils/datetime';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  root: {
    minWidth: 250,
  },
  pos: {
    marginBottom: 5,
  },
  title: {
    fontSize: 13,
  },
  datePos: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: 0,
  },
  dateText: {
    fontSize: 15,
    marginTop: 20,
  },
  statusPos: {
    display: 'flex',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
  },
  datetext: {
    fontSize: 14,
    paddingLeft: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(0.5),
  },
  pollingProgress: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  dialog: {
    padding: '2rem',
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
};

const createAssignmentRepo = (assignment, enqueueSnackbar) => () => {
  axios.post(`/api/public/repos/create/${assignment.id}`).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

export default function AssignmentCard({
  assignment,
  setSelectedTheia,
  runAssignmentPolling,
  setRunAssignmentPolling,
  setPollingAssignmentId,
}) {
  const classes = useStyles();
  const {
    id,
    name,
    due_date,
    course: {course_code},
    has_submission,
    ide_enabled,
    has_repo,
    repo_url,
    past_due,
    hide_due_date,
    github_repo_required,
    // accept_late,
  } = assignment;

  const {enqueueSnackbar} = useSnackbar();

  const [timeLeft] = useState(remainingTime(due_date));
  const [isOpen, setIsOpen] = useState(false);

  const timerComponents = [];
  Object.keys(timeLeft).forEach((interval) => {
    if (!timeLeft[interval]) {
      return;
    }
    timerComponents.push( // decorate
      <span>
        {timeLeft[interval]} {interval} left
      </span>,
    );
  });

  const handleGithubCreateLinkClicked = useCallback(() => {
    setRunAssignmentPolling(true);
    setPollingAssignmentId(id);
  }, [setRunAssignmentPolling, setPollingAssignmentId, id]);

  const githubLinkEnabled = github_repo_required;
  const ideLinkEnabled = ide_enabled && (has_repo || runAssignmentPolling || !github_repo_required);

  return (
    <Card className={classes.root}>
      <CardActionArea
        component={Link}
        to={`/courses/assignments/submissions?assignmentId=${id}`}>
        <CardContent>

          <div style={{display: 'flex', justifyContent: 'space-between'}}>
            <Typography variant={'subtitle1'} color="textSecondary" gutterBottom>
              {course_code}
            </Typography>
            {!assignment.visible_to_students && (
              <Tooltip title={'Not visible to students'}>
                <VisibilityOffIcon style={{color: grey[500]}}/>
              </Tooltip>
            )}
          </div>

          <Typography variant={'h6'}>
            {name}
          </Typography>

          {!hide_due_date && (
            <React.Fragment>
              <div className={classes.datePos}>
                <EventNoteIcon style={{marginRight: 7}}/>
                <p className={classes.dateText}>Due: {nonStupidDatetimeFormat(new Date(due_date))}</p>
              </div>

              <div className={classes.statusPos} style={has_submission ? {} : {color: red[500]}}>
                {has_submission ?
                  <CheckCircleIcon style={{color: green[500], marginRight: 6}}/> :
                  <AlarmIcon style={{marginRight: 7}}/>
                }

                <p className={classes.statusText}>
                  {has_submission ?
                    'Assignment Submitted' :
                    timerComponents.length ?
                      timerComponents[0] :
                      'Past Due'}
                </p>
              </div>
            </React.Fragment>
          )}
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Box display="flex" flexDirection="column" width={'100%'}>
          <Button
            size={'medium'}
            variant={'contained'}
            color={'primary'}
            className={classes.button}
            startIcon={<i className="devicon-vscode-plain" />}
            disabled={!ideLinkEnabled}
            onClick={() => setSelectedTheia(assignment)}
          >
            Anubis Cloud IDE
          </Button>
          {runAssignmentPolling && <CircularProgress size={24} className={classes.pollingProgress}/>}
          {githubLinkEnabled && (
            <React.Fragment>
              {!has_repo && (
                <Button
                  size={'medium'}
                  variant={'contained'}
                  color={'primary'}
                  startIcon={<GitHubIcon/>}
                  className={classes.button}
                  onClick={createAssignmentRepo(assignment, enqueueSnackbar)}
                  onClickCapture={handleGithubCreateLinkClicked}
                >
                  Create assignment repo
                </Button>
              )}

              {has_repo && (
                <Button
                  size={'medium'}
                  variant={'contained'}
                  color={'primary'}
                  startIcon={<GitHubIcon/>}
                  className={classes.button}
                  component={'a'}
                  href={repo_url}
                  target={'_blank'}
                >
                  Go to assignment repo
                </Button>
              )}
            </React.Fragment>
          )}
          {assignment.description &&
          <Button
            size='small'
            variant='contained'
            color='primary'
            startIcon={<DescriptionIcon/>}
            className={classes.button}
            component='a'
            onClick={() => setIsOpen(true)}
          >
            View Description
          </Button>
          }
          <Dialog
            onClose={() => setIsOpen(false)}
            open={isOpen}
          >
            <div className={classes.dialog}>
              <Typography variant='h6'>Assignment - {assignment.name}</Typography>
              <ReactMarkdown>
                {assignment.description}
              </ReactMarkdown>
            </div>
          </Dialog>
        </Box>
      </CardActions>
    </Card>
  );
}
