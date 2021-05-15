import React, {useEffect, useState} from 'react';
import Paper from '@material-ui/core/Paper';
import Slider from '@material-ui/core/Slider';
import Typography from '@material-ui/core/Typography';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';

import {
  DiscreteColorLegend,
  Hint,
  HorizontalGridLines,
  LineMarkSeries,
  VerticalGridLines,
  XAxis,
  XYPlot,
  FlexibleWidthXYPlot,
  YAxis,
} from 'react-vis';

const useStyles = makeStyles((theme) => ({
  legend: {
    color: theme.palette.text.primary,
  },
  typography: {
    paddingLeft: theme.spacing(1),
  },
}));

export default function StudentHistory({testResults: rawTestResults, buildResults: rawBuildResults}) {
  const classes = useStyles();
  const [hint, setHint] = useState(null);
  const [width, setWidth] = useState(0);
  const [testResults, setTestResult] = useState([]);
  const [buildResults, setBuildResult] = useState([]);

  useEffect(() => {
    setTestResult(rawTestResults.map(({x, ...y}) => ({x: new Date(x), ...y})));
    setBuildResult(rawBuildResults.map(({x, ...y}) => ({x: new Date(x), ...y})));
    setWidth(rawBuildResults.length);
  }, [rawBuildResults, rawTestResults]);

  const updateValues = (width) => {
    const tsize = rawTestResults.length;
    setTestResult(rawTestResults.slice(tsize-width, tsize-1).map(({x, ...y}) => ({x: new Date(x), ...y})));

    const bsize = rawBuildResults.length;
    setBuildResult(rawBuildResults.slice(bsize-width, bsize-1).map(({x, ...y}) => ({x: new Date(x), ...y})));

    setWidth(width);
  };

  return (
    <Paper style={{display: 'flex'}}>
      <Grid container spacing={2} direction={'column'} justify={'space-between'} style={{width: 150}}>
        <Grid item>
          <style>
            {`.rv-discrete-color-legend-item {color: #fff;}`}
          </style>
          <DiscreteColorLegend className={classes.legend} items={[
            {title: 'Test Results', color: 'blue'},
            {title: 'Build Results', color: 'green'},
          ]}/>
        </Grid>
        <Grid item>
          <Typography id="discrete-slider-small-steps" className={classes.typography} gutterBottom>
            Items to Show
          </Typography>
          <Slider
            className={classes.slider}
            defaultValue={width}
            value={width}
            getAriaValueText={''}
            aria-labelledby="discrete-slider-small-steps"
            step={5}
            onChange={(_, value) => updateValues(value)}
            min={5}
            max={rawTestResults.length}
            valueLabelDisplay="auto"
          />
        </Grid>
      </Grid>
      <FlexibleWidthXYPlot
        animation
        xType="time" height={300}
      >
        <VerticalGridLines/>
        <HorizontalGridLines/>
        <XAxis title={'time'}/>
        <YAxis/>

        {/* Tests */}
        <LineMarkSeries
          animation
          curve={'curveMonotoneX'}
          onValueMouseOver={(value) => setHint(value)}
          onValueMouseOut={() => setHint(null)}
          style={{strokeWidth: '2px'}}
          lineStyle={{stroke: 'blue'}}
          markStyle={{stroke: 'blue'}}
          data={testResults}
        />

        {/* Builds */}
        <LineMarkSeries
          animation
          curve={'curveMonotoneX'}
          onValueMouseOver={(value) => setHint(value)}
          onValueMouseOut={() => setHint(null)}
          style={{strokeWidth: '2px'}}
          lineStyle={{stroke: 'green'}}
          markStyle={{stroke: 'green'}}
          data={buildResults}
        />

        {hint ? <Hint value={hint}/> : null}
      </FlexibleWidthXYPlot>
    </Paper>
  );
}
