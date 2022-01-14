import React from 'react';
import Chip from '@material-ui/core/Chip';
import {makeStyles} from '@material-ui/core/styles';
import useQuery from '../../hooks/useQuery';

const useStyles = makeStyles((theme) => ({
  card: {
    minWidth: 275,
  },
}));

export default function Error({show, onDelete}) {
  const classes = useStyles();
  const query = useQuery();

  if (!show) return null;

  return (
    <div className={classes.chip}>
      <Chip
        label={query.get('error')}
        onDelete={onDelete}
        color="secondary"
      />
    </div>
  );
}
