import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import React from 'react';

export default function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link href={'/api/public/memes/'} target={'_blank'}>
        Memes
      </Link>{' '}
      {new Date().getFullYear()}
    </Typography>
  );
}
