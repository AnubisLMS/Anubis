import React from 'react';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Zoom from '@mui/material/Zoom';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';


const data = {
  severity: 'info',
  title: 'Interested in security at Anubis?',
  content: 'Come to hack night at the OSIRIS Lab (370 Jay Street, floor 10 room 66) March 9th at 6PM. The creator ' +
    'of Anubis and will be giving ' +
    'a presentation on container security and how it applies to Anubis. Come learn how you secure a modern, ' +
    'large scale distributed system with hundreds of active users who all have a shell.',
  action: {
    href: 'https://discord.gg/GEYtaATJHs',
    label: 'OSIRIS discord',
  },
};

export default function GenericAd() {
  return (
    <Zoom in>
      <Alert
        severity={data.severity}
        variant="outlined"
        sx={{mt: 2, mb: 2}}
        action={
          <React.Fragment>
            {data.action && (
              <Button
                sx={{m: 2}}
                variant={'contained'}
                color={'primary'}
                startIcon={<ExitToAppIcon/>}
                href={data.action.href}
                target="_blank"
                rel="noreferrer"
              >
                {data.action.label}
              </Button>
            )}
          </React.Fragment>
        }
      >
        <AlertTitle sx={{fontSize: 22}}>
          <strong>
            {data.title}
          </strong>
        </AlertTitle>
        <Typography variant={'body1'}>
          {data.content}
        </Typography>
      </Alert>
    </Zoom>
  );
}
