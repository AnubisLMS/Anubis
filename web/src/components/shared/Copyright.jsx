import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import React from 'react';

export default function Copyright() {
  const {REACT_APP_GIT_TAG} = process.env;
  return (
    <Box>
      <Typography variant="body2" color="textSecondary" align="center">
        {'Copyright © '}
        <Link href={'/api/public/memes/'} target={'_blank'}>
        Memes
        </Link>{' '}
        {new Date().getFullYear()}
      </Typography>
      <Typography variant={'body2'} color={'textSecondary'} sx={{fontSize: 10}}>
        {REACT_APP_GIT_TAG}
      </Typography>
    </Box>
  );
}
