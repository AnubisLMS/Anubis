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


const useStyles = makeStyles((theme) => ({
  root: {
    flexShrink: 0,
    marginLeft: theme.spacing(2.5),
  },
  instructions: {
    paddingTop: theme.spacing(1),
    paddingLeft: theme.spacing(1),
  },
  available: {
    display: 'inline',
  },
}));

export default function IDEHeader({session_available}) {
  const classes = useStyles();

  return (
    <React.Fragment>
      <Typography variant="h6">
        Anubis Cloud IDE
      </Typography>
      <Tooltip
        title={session_available ? 'Anubis Cloud IDE Available' : 'Anubis Cloud IDE Not Available'}
        className={classes.available}
      >
        <IconButton>
          {session_available ?
            <CheckOutlinedIcon style={{color: green[500]}} fontSize={'large'}/> :
            <CloseOutlinedIcon style={{color: red[500]}} fontSize={'large'}/>}
        </IconButton>
      </Tooltip>
      <Typography variant={'body1'} className={classes.available}>
        {session_available ?
          'Anubis Cloud IDE session resources are currently available for use' :
          'Anubis Cloud IDE session resources are currently not available for use'}
      </Typography>
      <Tooltip title={session_available ?
        'Anubis Cloud IDE session resources are currently available for use. Go to the assignment ' +
        'page to select which assignment you would like to launch an Anubis Cloud IDE for.' :
        'The maximum quota of Anubis Cloud IDE sessions on our servers has been reached. ' +
        'At this time, we cannot allocate more sessions until others have ended.'}>
        <IconButton>
          <HelpOutlineOutlinedIcon fontSize={'small'}/>
        </IconButton>
      </Tooltip>
    </React.Fragment>
  );
}
