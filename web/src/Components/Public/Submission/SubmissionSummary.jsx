import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import green from '@material-ui/core/colors/green';
import CancelIcon from '@material-ui/icons/Cancel';
import red from '@material-ui/core/colors/red';
import ListItemText from '@material-ui/core/ListItemText';
import AccessTimeIcon from '@material-ui/icons/AccessTime';
import RefreshIcon from '@material-ui/icons/Refresh';
import CircularProgress from '@material-ui/core/CircularProgress';
import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import TableCell from '@material-ui/core/TableCell';
import Divider from '@material-ui/core/Divider';
import {useSnackbar} from 'notistack';
import clsx from 'clsx';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '75%',
  },
  title: {
    margin: theme.spacing(1),
  },
  divider: {
    backgroundColor: '#999',
  },
  inline: {
    display: 'inline',
  },
  margin: {
    margin: theme.spacing(1),
  },
}));

export default function SubmissionSummary({submission, regrade, stop = false}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  if (!submission) {
    return null;
  }

  if (typeof submission === 'string') {
    return (
      <div>
        <Tooltip title={'No submission was captured for this student.'}>
          <CancelIcon color={'secondary'}/>
        </Tooltip>
        <Typography variant={'h5'} className={clsx(classes.inline, classes.margin)}>
          {submission}
        </Typography>
      </div>
    );
  }

  const testsPassed = submission.tests.filter((test) => test.result.passed).length;
  const totalTests = submission.tests.length;

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardContent>
          {/* Assignment name */}
          <Typography gutterBottom variant={'h6'} className={classes.title}>
            {submission.assignment_name}
          </Typography>
          <Divider variant={'middle'} className={classes.divider}/>

          <List>
            {/* On time*/}
            <ListItem>
              <ListItemIcon>
                <Tooltip title={submission.on_time ?
                  'Submitted On Time' :
                  'Submitted Late'}>
                  <IconButton component="div">
                    {submission.on_time ?
                      <CheckCircleIcon style={{color: green[500]}}/> :
                      <CancelIcon style={{color: red[500]}}/>}
                  </IconButton>
                </Tooltip>
              </ListItemIcon>
              <ListItemText primary={submission.on_time ?
                'Submitted On Time' :
                'Submitted Late'}/>
            </ListItem>

            {/* Submission time */}
            <ListItem>
              <ListItemIcon>
                <Tooltip title={`Submitted at ${submission.created}`}>
                  <IconButton component="div">
                    <AccessTimeIcon color={'primary'}/>
                  </IconButton>
                </Tooltip>
              </ListItemIcon>
              <ListItemText primary={submission.created}/>
            </ListItem>

            {/* Tests passed / total tests */}
            <ListItem>
              <ListItemIcon>
                {!submission.processed ? (
                  <Tooltip title={'Submission is still processing!'}>
                    <IconButton>
                      <CircularProgress size="1em"/>
                    </IconButton>
                  </Tooltip>
                ) : (
                  <Tooltip title={testsPassed === totalTests ?
                    'All Tests Passed' :
                    'Not all tests passed'}>
                    <IconButton>
                      {testsPassed === totalTests ?
                        <CheckCircleIcon style={{color: green[500]}}/> :
                        <CancelIcon style={{color: red[500]}}/>}
                    </IconButton>
                  </Tooltip>
                )}
              </ListItemIcon>
              <ListItemText primary={
                `${testsPassed}/${totalTests}`
              }/>
            </ListItem>

            {/* Submission state */}
            <ListItem>
              <ListItemIcon>
                <Tooltip title={!submission.processed ? submission.state : 'regrade'}>
                  <IconButton component="div" onClick={() =>
                    regrade(submission.commitHash, enqueueSnackbar)}>
                    {(submission.processed && !stop) ?
                      <RefreshIcon color={'primary'}/> :
                      <CircularProgress size="1em"/>}
                  </IconButton>
                </Tooltip>
              </ListItemIcon>
              <ListItemText primary={submission.state}/>
            </ListItem>

          </List>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
