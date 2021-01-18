import React from 'react';

import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import CheckOutlinedIcon from '@material-ui/icons/CheckOutlined';
import green from '@material-ui/core/colors/green';
import CloseOutlinedIcon from '@material-ui/icons/CloseOutlined';
import red from '@material-ui/core/colors/red';
import HelpOutlineOutlinedIcon from '@material-ui/icons/HelpOutlineOutlined';
import {makeStyles} from '@material-ui/core/styles';
import clsx from 'clsx';


const useStyles = makeStyles((theme) => ({
  root: {
    marginBottom: theme.spacing(2),
  },
  inline: {
    display: 'inline',
  },
  smallText: {
    fontSize: 13,
  },
}));

export default function IDEHeader({sessionsAvailable}) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Tooltip title={sessionsAvailable ?
        'Anubis Cloud IDE session resources are currently available for use. Go to the assignment ' +
        'page to select which assignment you would like to launch an Anubis Cloud IDE for.' :
        'The maximum quota of Anubis Cloud IDE sessions on our servers has been reached. ' +
        'At this time, we cannot allocate more sessions until others have ended.'}>
        <IconButton>
          <HelpOutlineOutlinedIcon fontSize={'small'}/>
        </IconButton>
      </Tooltip>
      <Tooltip title={sessionsAvailable ? 'Anubis Cloud IDE Available' : 'Anubis Cloud IDE Not Available'}>
        <IconButton>
          {sessionsAvailable ?
            <CheckOutlinedIcon style={{color: green[500]}} fontSize={'small'}/> :
            <CloseOutlinedIcon style={{color: red[500]}} fontSize={'small'}/>}
        </IconButton>
      </Tooltip>
      <Typography variant={'body1'} className={clsx(classes.inline, classes.smallText)}>
        {sessionsAvailable ?
          'Session resources available' :
          'Session resources are not available'}
      </Typography>
    </div>
  );
}
