import React from 'react';

import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';


export default function StandardLayout({title, description = '', children = null}) {
  if (typeof description === 'string') {
    description = [description];
  }

  if (!Array.isArray(description)) {
    description = [];
  }

  return (
    <Grid container spacing={4} justifyContent={'center'}>
      <Grid item xs={12} md={11}>
        {title &&
          <Typography variant="h5">
            {title}
          </Typography>
        }
      </Grid>
      <Grid item/>
      <Grid item xs={12} md={11}>
        {children}
      </Grid>
    </Grid>
  );
}
