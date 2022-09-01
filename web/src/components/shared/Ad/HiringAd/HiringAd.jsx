import React from 'react';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Button from '@mui/material/Button';
import Zoom from '@mui/material/Zoom';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

export default function HiringAd() {
  return (
    <Zoom in>
      <Alert
        severity="success"
        variant="outlined"
        sx={{m: 1}}
        action={
          <Button
            sx={{m: 1}}
            variant={'contained'}
            color={'primary'}
            startIcon={<ExitToAppIcon/>}
            href="https://github.com/AnubisLMS/InterviewProject"
            target="_blank"
            rel="noreferrer"
          >
            Apply
          </Button>
        }
      >
        <AlertTitle>{'Anubis is Hiring!'}</AlertTitle>
        Know or want to know about full stack engineering, or distributed computing? Anubis is a massively
        advanced modern system that is reaching hundreds of your peers built by students at Tandon.
      </Alert>
    </Zoom>
  );
}
