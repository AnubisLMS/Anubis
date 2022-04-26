import React from 'react';
import clsx from 'clsx';

import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import {useStyles} from './ListHeader.styles';

const ListHeader = ({sections}) => {
  const classes = useStyles();
  return (
    <Grid container className={classes.container}>
      {sections && sections.map((section, index) => (
        <Grid
          key={`${section}-${index}`}
          item xs={Math.floor(12/ sections.length)}
          className={
            index === 0 ? clsx(classes.sectionBlock, classes.start) :
              index === sections.length - 1 ? clsx(classes.sectionBlock, classes.end) :
                clsx(classes.sectionBlock, classes.center)}
        >
          <Typography >{section}</Typography>
        </Grid>
      ))}
    </Grid>
  );
};

export default ListHeader;
