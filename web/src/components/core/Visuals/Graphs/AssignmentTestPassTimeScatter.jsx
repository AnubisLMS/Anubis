import React, {useState} from 'react';
import {XYPlot, XAxis, YAxis, VerticalGridLines, HorizontalGridLines, MarkSeries, Hint} from 'react-vis';


export default function AssignmentTestTimes({title, data}) {
  const [hoverNode, setHoverNode] = useState(null);

  return (
    <XYPlot
      // xDomain={[0, 10]}
      width={300}
      height={300}
      onMouseLeave={() => setHoverNode(null)}
    >
      <VerticalGridLines tickTotal={10}/>
      <HorizontalGridLines tickTotal={10}/>
      <XAxis title={'Hours'}/>
      <YAxis title={'Number of students'}/>
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
  );
}

