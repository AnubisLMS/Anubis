import React, {useState} from 'react';

import makeStyles from '@mui/styles/makeStyles';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';

import AssignmentTestPassTimeScatter from './Graphs/AssignmentTestPassTimeScatter';
import AssignmentTestPassCountRadial from './Graphs/AssignmentTestPassCountRadial';

const useStyles = makeStyles((theme) => ({
  graphPaper: {
    margin: theme.spacing(0, 1),
  },
  plot: {
    display: 'flex',
    flexDirection: 'column',
    margin: theme.spacing(1),
  },
  title: {
    fontSize: 14,
    marginBottom: theme.spacing(1),
    marginLeft: theme.spacing(1),
  },
}));

const modes = ['pie', 'scatter'];

export default function AssignmentTestsPaper({title, pass_time_scatter, pass_count_radial}) {
  const classes = useStyles();
  const [mode, setMode] = useState(0);

  const handleChange = (_, newValue) => {
    setMode(newValue);
  };

  return (
    <Paper key={title} className={classes.graphPaper}>
      <Tabs
        value={mode}
        indicatorColor="primary"
        textColor="primary"
        onChange={handleChange}
        aria-label="disabled tabs example"
      >
        <Tab label="Pie"/>
        <Tab label="Scatter"/>
      </Tabs>
      <div className={classes.plot}>
        <Typography className={classes.title}>
          {title}
        </Typography>
        {mode === 0 ? <AssignmentTestPassCountRadial data={pass_count_radial}/> : null}
        {mode === 1 ? <AssignmentTestPassTimeScatter data={pass_time_scatter}/> : null}
      </div>
    </Paper>
  );
}
