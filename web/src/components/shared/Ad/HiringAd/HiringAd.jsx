import React from 'react';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Button from '@mui/material/Button';
import Zoom from '@mui/material/Zoom';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import Typography from '@mui/material/Typography';

export default function HiringAd() {
  return (
    <Zoom in>
      <Alert
        severity="success"
        variant="outlined"
        sx={{mt: 2, mb: 2}}
        action={
          <Button
            sx={{m: 2}}
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
        <AlertTitle sx={{fontSize: 22}}>
          <strong>
            {'Anubis is Hiring!'}
          </strong>
        </AlertTitle>
        <Typography variant={'body1'}>
          Know or want to know about full stack engineering, or distributed computing?
          Anubis is a massively advanced modern system that is reaching hundreds of
          your peers built entirely by students at Tandon.
        </Typography>
      </Alert>
    </Zoom>
  );
}
