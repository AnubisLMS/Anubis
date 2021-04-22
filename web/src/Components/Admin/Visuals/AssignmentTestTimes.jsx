import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';

import {XYPlot, XAxis, YAxis, VerticalGridLines, HorizontalGridLines, MarkSeries, Hint} from 'react-vis';
import 'react-vis/dist/style.css';

const useStyles = makeStyles((theme) => ({
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

export default function AssignmentTestTimes({title, data}) {
  const classes = useStyles();
  const [hoverNode, setHoverNode] = useState(null);

  return (
    <div className={classes.plot}>
      <Typography className={classes.title}>
        {title}
      </Typography>
      <XYPlot
        // xDomain={[0, 10]}
        width={300}
        height={300}
        onMouseLeave={() => setHoverNode(null)}
      >
        <VerticalGridLines tickTotal={10}/>
        <HorizontalGridLines tickTotal={10}/>
        <XAxis />
        <YAxis />
        <MarkSeries
          animated={true}
          strokeWidth={2}
          opacity="0.8"
          sizeRange={[0, 5]}
          data={data}
          seriesId={title}
          opacityType={'literal'}
          onValueMouseOver={(d) => setHoverNode(d)}
        />
        {hoverNode !== null ? (
          <Hint value={hoverNode}/>
        ) : null}
      </XYPlot>
    </div>
  );
}

