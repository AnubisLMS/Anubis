import React from 'react';

import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';


export default function StandardLayout({title, description = '', children = null}) {
  if (typeof description === 'string') {
    description = [description];
  }

  if (!Array.isArray(description)) {
    description = [];
  }

  return (
    <Grid container spacing={4} justify={'center'}>
      <Grid item xs={12} md={11}>
        {title &&
          <Typography variant="h5">
            {title}
          </Typography>
        }
        {/* {description.map((text, index) => (
          <Typography variant={'subtitle1'} color={'textSecondary'} key={`desc-${title}-${index}`}>
            {text}
          </Typography>
        ))} */}
      </Grid>
      <Grid item/>
      <Grid item xs={12} md={11}>
        {children}
      </Grid>
    </Grid>
  );
}
