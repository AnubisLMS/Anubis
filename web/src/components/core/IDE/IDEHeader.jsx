import React from 'react';

import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import CheckOutlinedIcon from '@mui/icons-material/CheckOutlined';
import green from '@mui/material/colors/green';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import red from '@mui/material/colors/red';
import HelpOutlineOutlinedIcon from '@mui/icons-material/HelpOutlineOutlined';
import {makeStyles} from '@mui/material/styles';
import clsx from 'clsx';


const useStyles = makeStyles((theme) => ({
  root: {
    marginBottom: theme.spacing(2),
    display: 'flex',
    alignItems: 'center',
  },
  smallText: {
    fontSize: 13,
  },
}));

export default function IDEHeader({sessionsAvailable}) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Tooltip title={sessionsAvailable ? 'Anubis Cloud IDE Available' : 'Anubis Cloud IDE Not Available'}>
        <IconButton>
          {sessionsAvailable ?
            <CheckOutlinedIcon style={{color: green[500]}} fontSize={'small'}/> :
            <CloseOutlinedIcon style={{color: red[500]}} fontSize={'small'}/>}
        </IconButton>
      </Tooltip>
      <Typography variant={'body1'} className={classes.smallText}>
        {sessionsAvailable ?
          'Session resources available' :
          'Session resources are not available'}
      </Typography>
      <Tooltip title={sessionsAvailable ?
        'Anubis Cloud IDE session resources are currently available for use. Go to the assignment ' +
        'page to select which assignment you would like to launch an Anubis Cloud IDEfor.' :
        'The maximum quota of Anubis Cloud IDE sessions on our servers has been reached. ' +
        'At this time, we cannot allocate more sessions until others have ended.'}>
        <IconButton>
          <HelpOutlineOutlinedIcon fontSize={'small'}/>
        </IconButton>
      </Tooltip>
    </div>
  );
}
