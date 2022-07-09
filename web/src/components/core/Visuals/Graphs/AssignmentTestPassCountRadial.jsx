import React, {useState} from 'react';
import {RadialChart, Hint} from 'react-vis';

import Typography from '@mui/material/Typography';

export default function AssignmentTestCountRadial({data}) {
  const [hoverNode, setHoverNode] = useState(null);

  return (
    <RadialChart
      innerRadius={100}
      radius={140}
      colorType="literal"
      data={data}
      width={300}
      height={300}
      padAngle={0.04}
      getAngle={(d) => d.theta}
      onValueMouseOver={(d) => setHoverNode(d)}
      onSeriesMouseOut={() => setHoverNode(null)}
    >
      {hoverNode !== null && (
        <Hint
          value={hoverNode}
        >
          <Typography style={{color: 'white'}}>
            {hoverNode.theta} {hoverNode.label}
          </Typography>
        </Hint>
      )}
    </RadialChart>
  );
}
