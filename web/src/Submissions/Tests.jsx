import React from 'react';
import CheckIcon from '@material-ui/icons/Check';
import CloseIcon from '@material-ui/icons/Close';
import {makeStyles} from "@material-ui/core/styles";
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from "@material-ui/core/Tooltip";

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
  },
  title: {
    padding: theme.spacing(0.5),
  }
}));

export default function Tests({tests, reports}) {
  const classes = useStyles();

  if (!tests || !reports) {
    return (
      <div/>
    );
  }

  const t = tests.split('\n\n');
  const r = reports.map((elem) => {
    elem.logs = t.find(stdout => (
      stdout.trim().startsWith(elem.testname)
    ));
    return elem;
  }).sort((t1, t2) => t1.testname > t2.testname);

  return (
    <div className={classes.root}>
      {r.map(({testname, passed, errors, logs}) => (
        <ExpansionPanel key={testname}>
          <ExpansionPanelSummary
            expandIcon={<ExpandMoreIcon/>}
            aria-label="Expand"
            aria-controls={`${testname}-content`}
            id={`${testname}-content-id`}
          >
            <IconButton edge={'start'}>
              {passed ? (
                <Tooltip title={'Passed'}>
                  <CheckIcon
                    color={'primary'}
                    className={classes.icon}
                    fontSize={'small'}
                  />
                </Tooltip>
              ) : (
                <Tooltip title={''}>
                  <CloseIcon
                    color={'secondary'}
                    className={classes.icon}
                    fontSize={'small'}
                  />
                </Tooltip>
              )}
            </IconButton>
            <Typography className={classes.title} variant={'subtitle1'}>
              {testname}
            </Typography>
          </ExpansionPanelSummary>
          <ExpansionPanelDetails>
            <div>
              {logs.split('\n').map((line, index) => (
                <Typography
                  key={index}
                  variant={'body1'}
                  color={'textSecondary'}
                  width={100}
                >
                  {line}
                </Typography>
              ))}
            </div>
          </ExpansionPanelDetails>
        </ExpansionPanel>
      ))}
    </div>
    // <Typography variant={'h5'} component={'h2'}>
    //   Logs
    // </Typography>
    // {tests ? tests.trim().split('\n').map((line, index) => (
    //   <Typography
    //     className={classes.pos}
    //     // component="pre"
    //     variant={"body1"}
    //     color={"textSecondary"}
    //     width={100}
    //     key={`line-${index}`}
    //   >
    //     {line}
    //   </Typography>
    // )) : null}
  );
}