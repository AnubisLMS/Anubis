import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import CircularProgress from '@material-ui/core/CircularProgress';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import green from '@material-ui/core/colors/green';
import CancelIcon from '@material-ui/icons/Cancel';
import Fab from '@material-ui/core/Fab';
import AssessmentIcon from '@material-ui/icons/Assessment';
import HighlightOffIcon from '@material-ui/icons/HighlightOff';
import {Tooltip} from '@material-ui/core';
import IconButton from '@material-ui/core/IconButton';

const useStyles = makeStyles((theme) => ({
  heading: {
    padding: theme.spacing(2),
    alignItems: 'center',
    display: 'flex',
  },
  hiddenIcon: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  wrapper: {
    margin: theme.spacing(1),
    position: 'relative',
  },
  fabProgress: {
    color: green[500],
    position: 'absolute',
    top: -6,
    left: -6,
    zIndex: 1,
  },
}));


export default function SubmissionTests({tests, stop}) {
  const classes = useStyles();

  if (!tests) {
    return null;
  }

  return (
    <React.Fragment>
      {tests.map((test, index) => (
        <Accordion key={`test-${index}`}>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon/>}
            aria-controls="panel2a-content"
            id="panel2a-header"
          >
            <div className={classes.wrapper}>
              <Fab
                aria-label="save"
                color={stop ? 'secondary' : (test.result.passed === false ? 'secondary' : 'primary')}
              >
                {stop ? (
                  <CancelIcon/>
                ) : (
                  <React.Fragment>
                    {test.result.passed === null ? (
                      <AssessmentIcon/>
                    ) : (test.result.passed === true) ? (
                      <CheckCircleIcon/>
                    ) : (test.result.passed === false) ? (
                      <CancelIcon/>
                    ) : null}
                  </React.Fragment>
                )}
              </Fab>
              {stop ? null : (
                test.result.passed === null && <CircularProgress size={68} className={classes.fabProgress}/>
              )}
            </div>
            <Typography className={classes.heading}>{test.test.name}</Typography>
            {test.test.hidden ? (
              <div className={classes.hiddenIcon}>
                <Tooltip title={'Test hidden to students'}>
                  <IconButton>
                    <HighlightOffIcon/>
                  </IconButton>
                </Tooltip>
              </div>
            ) : null}
          </AccordionSummary>
          <AccordionDetails>
            <div>
              <Typography key={'message'} variant={'h5'} className={classes.heading}>
                {test.result.message}
              </Typography>
              {test.result.passed !== null && !!test.result.stdout ?
                test.result.stdout.trim().split('\n')
                  .map((line, index) => (
                    line.trim().length !== 0 ?
                      <Typography
                        variant={'body1'}
                        color={'textSecondary'}
                        width={100}
                        key={`line-${index}`}
                      >
                        {line}
                      </Typography> :
                      <br/>
                  )) :
                null}
            </div>
          </AccordionDetails>
        </Accordion>
      ))}
    </React.Fragment>
  );
}
