import React from 'react';
import Typography from '@material-ui/core/Typography';
import Accordion from '@material-ui/core/Accordion';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import CircularProgress from '@material-ui/core/CircularProgress';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import BuildIcon from '@material-ui/icons/Build';
import Fab from '@material-ui/core/Fab';
import {makeStyles} from '@material-ui/core/styles';
import green from '@material-ui/core/colors/green';

const useStyles = makeStyles((theme) => ({
  heading: {
    padding: theme.spacing(2),
    display: 'flex',
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

export default function SubmissionBuild({build, stop}) {
  const classes = useStyles();

  if (!build) {
    return null;
  }

  return (
    <Accordion>
      <AccordionSummary
        expandIcon={<ExpandMoreIcon/>}
        aria-controls="panel1a-content"
        id="panel1a-header"
      >
        <div className={classes.wrapper}>
          <Fab
            aria-label="save"
            color={build.passed === false ? 'secondary' : 'primary'}
          >
            {build.passed === null ? (
              <BuildIcon/>
            ) : (build.passed === true && !stop) ? (
              <CheckCircleIcon/>
            ) : (build.passed === false || stop) ? (
              <CancelIcon/>
            ) : null}
          </Fab>
          {build.passed === null && <CircularProgress size={68} className={classes.fabProgress}/>}
        </div>

        <Typography className={classes.heading}>Build</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <div>
          {build.stdout ?
            build.stdout.trim().split('\n')
              .map((line, index) => (
                <Typography
                  variant={'body1'}
                  color={'textSecondary'}
                  width={100}
                  key={`line-${index}`}
                >
                  {line}
                </Typography>
              )) :
            null}
        </div>
      </AccordionDetails>
    </Accordion>
  );
}
