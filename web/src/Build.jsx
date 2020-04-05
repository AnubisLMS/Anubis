import React from 'react';
import Typography from '@material-ui/core/Typography';
import {makeStyles} from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import IconButton from '@material-ui/core/IconButton';
import Tooltip from "@material-ui/core/Tooltip";
import CheckIcon from "@material-ui/icons/Check";

const useStyles = makeStyles(theme => ({
  root: {
    width: '100%',
  },
  title: {
    padding: theme.spacing(0.5),
  }
}));

export default function Build({data}) {
  const classes = useStyles();

  if (!data) {
    return (
      <div/>
    );
  }

  return (
    <ExpansionPanel className={classes.root}>
      <ExpansionPanelSummary
        expandIcon={<ExpandMoreIcon/>}
        aria-label="Expand"
        aria-controls={`build`}
        id={`build-panel`}
      >
        <IconButton edge={'start'}>
          <Tooltip title={'Build Succeeded'}>
            <CheckIcon
              color={'primary'}
              fontSize={'small'}
            />
          </Tooltip>
        </IconButton>
        <Typography className={classes.title} variant={'subtitle1'}>
          build
        </Typography>
      </ExpansionPanelSummary>
      <ExpansionPanelDetails>
        <div>
          {data ? data.trim().split('\n').map((line, index) => (
            <Typography
              variant={"body1"}
              color={"textSecondary"}
              width={100}
              key={`line-${index}`}
            >
              {line}
            </Typography>
          )) : null}
        </div>
      </ExpansionPanelDetails>
    </ExpansionPanel>
  )
}