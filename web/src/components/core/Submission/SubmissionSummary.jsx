import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import green from '@mui/material/colors/green';
import CancelIcon from '@mui/icons-material/Cancel';
import red from '@mui/material/colors/red';
import ListItemText from '@mui/material/ListItemText';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RefreshIcon from '@mui/icons-material/Refresh';
import CircularProgress from '@mui/material/CircularProgress';
import React from 'react';
import makeStyles from '@mui/styles/makeStyles';
import Divider from '@mui/material/Divider';
import {useSnackbar} from 'notistack';
import clsx from 'clsx';
import Fab from '@mui/material/Fab';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
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

export default function SubmissionSummary({submission, regrade, stop}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  if (!submission) {
    return null;
  }

  if (typeof submission === 'string') {
    return (
      <div>
        <Tooltip title={'No submission was captured for this student.'}>
          <CancelIcon color={'error'}/>
        </Tooltip>
        <Typography variant={'h5'} className={clsx(classes.inline, classes.margin)}>
          {submission}
        </Typography>
      </div>
    );
  }

  const testsPassed = submission.tests.filter((test) => test.result.passed).length;
  const totalTests = submission.tests.length;

  const ReloadIcon = () => (
    <Tooltip title={'regrade'}>
      <Fab
        onClick={() => regrade(submission.commitHash, enqueueSnackbar)}
        size={'small'}
        color={'primary'}
      >
        <RefreshIcon/>
      </Fab>
    </Tooltip>
  );

  const LoadingIcon = () => (
    <Tooltip title={submission.state}>
      <IconButton
        onClick={() => regrade(submission.commitHash, enqueueSnackbar)}
        size="large">
        <CircularProgress size="1em"/>
      </IconButton>
    </Tooltip>
  );

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
                  <IconButton component="div" size="large">
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
                  <IconButton component="div" size="large">
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
                    <IconButton size="large">
                      <CircularProgress size="1em"/>
                    </IconButton>
                  </Tooltip>
                ) : (
                  <Tooltip title={testsPassed === totalTests ?
                    'All Tests Passed' :
                    'Not all tests passed'}>
                    <IconButton size="large">
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
              {!!regrade ? (
                <ListItemIcon>
                  {stop ? <ReloadIcon/> : (
                    submission.processed ?
                      <ReloadIcon/> :
                      <LoadingIcon/>
                  )}
                </ListItemIcon>
              ) : null}
              <ListItemText primary={submission.state}/>
            </ListItem>

          </List>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
