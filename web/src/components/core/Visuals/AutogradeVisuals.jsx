import React from 'react';

import Grid from '@mui/material/Grid';

import AssignmentSundialPaper from './AssignmentSundialPaper';

export default function AutogradeVisuals() {
  return (
    <Grid container spacing={1} justifyContent={'center'} alignItems={'center'}>
      <Grid item>
        <AssignmentSundialPaper/>
      </Grid>
    </Grid>
  );
}
