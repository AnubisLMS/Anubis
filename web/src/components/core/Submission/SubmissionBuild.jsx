import React from 'react';
import Typography from '@mui/material/Typography';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CircularProgress from '@mui/material/CircularProgress';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import BuildIcon from '@mui/icons-material/Build';
import Fab from '@mui/material/Fab';
import makeStyles from '@mui/styles/makeStyles';
import green from '@mui/material/colors/green';

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
