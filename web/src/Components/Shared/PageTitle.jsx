import React from 'react';

import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';

const PageTitle = ({title = 'Anubis', description}) => {
  return (
    <Grid item xs={12}>
      <Typography variant='h6'>
        {title}
      </Typography>
      <Typography variant ='subtitle1' color = 'textSecondary'>
        {description}
      </Typography>
    </Grid>
  );
};

export default PageTitle;
