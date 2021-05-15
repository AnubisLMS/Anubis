import React, {useEffect, useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import {useSnackbar} from 'notistack';

import {LabelSeries, Sunburst} from 'react-vis';
import {EXTENDED_DISCRETE_COLOR_RANGE} from 'react-vis/es/theme';
import Typography from '@material-ui/core/Typography';

const LABEL_STYLE = {
  fontSize: '12px',
  color: '#fff',
  textAnchor: 'middle',
};

const useStyles = makeStyles((theme) => ({
  title: {
    fontSize: 18,
    paddingLeft: theme.spacing(1),
    paddingTop: theme.spacing(1),
  },
  typography: {
    padding: theme.spacing(1),
  },
}));

/**
 * Recursively work backwards from highlighted node to find path of valud nodes
 * @param {Object} node - the current node being considered
 * @returns {Array} an array of strings describing the key route to the current node
 */
function getKeyPath(node) {
  if (!node.parent) {
    return ['root'];
  }

  return [(node.data && node.data.name) || node.name].concat(
    getKeyPath(node.parent),
  );
}

/**
 * Recursively modify data depending on whether or not each cell has been selected by the hover/highlight
 * @param {Object} data - the current node being considered
 * @param {Object|Boolean} keyPath - a map of keys that are in the highlight path
 * if this is false then all nodes are marked as selected
 * @returns {Object} Updated tree structure
 */
function updateData(data, keyPath) {
  if (data.children) {
    data.children.map((child) => updateData(child, keyPath));
  }
  // add a fill to all the uncolored cells
  if (!data.hex) {
    data.style = {
      fill: EXTENDED_DISCRETE_COLOR_RANGE[5],
    };
  }
  data.style = {
    ...data.style,
    fillOpacity: keyPath && !keyPath[data.name] ? 0.2 : 1,
  };

  return data;
}

export default function AssignmentSundial({sundialData}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [pathValue, setPathValue] = useState(false);
  const [finalValue, setFinalValue] = useState('Anubis');
  const [data, setData] = useState({});
  const [decoratedData, setDecoratedData] = useState({});
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    setDecoratedData(updateData(sundialData, false));
    setData(updateData(sundialData, false));
  }, [sundialData]);

  return (
    <div className="basic-sunburst-example-wrapper">
      <Typography gutterBottom className={classes.title}>
        Anubis Autograde Sundial
      </Typography>
      <Sunburst
        animation
        className="basic-sunburst-example"
        hideRootNode
        onValueMouseOver={(node) => {
          if (clicked) {
            return;
          }
          const path = getKeyPath(node).reverse();
          const pathAsMap = path.reduce((res, row) => {
            res[row] = true;
            return res;
          }, {});
          setData(updateData(decoratedData, pathAsMap));
          setPathValue(path.join(' > '));
          setFinalValue(path[path.length - 1]);
        }}
        onValueMouseOut={() =>
          clicked ?
            () => {
            } : (function() {
              setPathValue(false);
              setFinalValue(false);
              setData(updateData(decoratedData, false));
            })()
        }
        onValueClick={() => setClicked(!clicked)}
        style={{
          stroke: '#ddd',
          strokeOpacity: 0.3,
          strokeWidth: '0.5',
        }}
        colorType="literal"
        getSize={(d) => d.value}
        getColor={(d) => d.hex}
        data={data}
        height={600}
        width={650}
      >
        {finalValue && (
          <LabelSeries
            data={[{x: 0, y: 0, label: finalValue, style: LABEL_STYLE}]}
          />
        )}
      </Sunburst>
      <Typography variant={'body2'} className={classes.typography}>
        {pathValue}
      </Typography>
    </div>
  );
}
