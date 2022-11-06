import React from 'react';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Button from '@mui/material/Button';
import Zoom from '@mui/material/Zoom';
import GitHubIcon from '@mui/icons-material/GitHub';
import Typography from '@mui/material/Typography';

export default function CodeServerAd() {
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
            startIcon={<GitHubIcon/>}
            href="https://github.com/AnubisLMS/IDE/issues/new"
            target="_blank"
            rel="noreferrer"
          >
            Open Issue
          </Button>
        }
      >
        <AlertTitle sx={{fontSize: 22}}>
          <strong>
            {'You may notice some changes...'}
          </strong>
        </AlertTitle>
        <Typography variant={'body1'}>
          We are in the progress of upgrading the IDE servers that we use from
          Theia to Code-Server. We are making this change so that we can better accommodate
          vscode extensions. There will be some visual changes that you will notice right away.{' '}
          <i>If you find that anything now doesn&#39;t work, please feel free to open an issue on
          our IDE repo on github.</i>
        </Typography>
      </Alert>
    </Zoom>
  );
}
