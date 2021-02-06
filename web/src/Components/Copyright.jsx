import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import React from 'react';

export default function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link href={'/api/public/memes/'}>
        Memes
      </Link>{' '}
      {new Date().getFullYear()}
    </Typography>
  );
}
