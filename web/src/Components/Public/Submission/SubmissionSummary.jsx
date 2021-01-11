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

const useStyles = makeStyles((theme) => ({
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
}));

export default function SubmissionSummary({submission, onTime, regrade, enqueueSnackbar}) {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            {submission.assignmentName}
          </Typography>
          <List>

            {/* On time*/}
            <ListItem>
              <ListItemIcon>
                <Tooltip title={onTime ?
                  'Submitted On Time' :
                  'Submitted Late'}>
                  <IconButton component="div">
                    {onTime ?
                      <CheckCircleIcon style={{color: green[500]}}/> :
                      <CancelIcon style={{color: red[500]}}/>}
                  </IconButton>
                </Tooltip>
              </ListItemIcon>
              <ListItemText primary={onTime ?
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

            {/* Submission state */}
            <ListItem>
              <ListItemIcon>
                <Tooltip title={!submission.processed ? submission.state : 'regrade'}>
                  <IconButton component="div" onClick={() =>
                    regrade(submission.commitHash, enqueueSnackbar)}>
                    {submission.processed ?
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
