import React from 'react';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Zoom from '@mui/material/Zoom';
import Typography from '@mui/material/Typography';

export default function MaintenanceAd() {
  return (
    <Zoom in>
      <Alert
        severity="info"
        variant="outlined"
        sx={{mt: 2, mb: 2}}
      >
        <AlertTitle sx={{fontSize: 22}}>
          <strong>
            {'Anubis IDEs will be unavailable from midnight to 1AM tonight (EST)'}
          </strong>
        </AlertTitle>
        <Typography variant={'body1'}>
          Some maintenance is required on our cluster that will make IDEs unavailable from 2022-12-06 00:00:00 EST to
          2022-12-06 01:00:00 EST. Please be advised that IDEs open at this time will be kicked off.
        </Typography>
      </Alert>
    </Zoom>
  );
}
