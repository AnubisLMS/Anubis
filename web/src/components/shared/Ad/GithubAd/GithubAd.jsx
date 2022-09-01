import React from 'react';

import {useStyles} from './GithubAd.styles';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import GitHubIcon from '@mui/icons-material/GitHub';
import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';

const GithubAd = () => {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardActionArea
        className={classes.actionArea}
        href="https://github.com/AnubisLMS"
        target="_blank"
        rel="noreferrer"
      >
        <Box className={classes.iconContainer}>
          <Box className={classes.iconInnerCircle}>
            <GitHubIcon className={classes.icon}/>
          </Box>
        </Box>
        <Typography className={classes.adTitle}>
          Interested in Contributing?
        </Typography>
        <Button className={classes.githubButton} variant={'contained'}>
          {'We\'re on Github'}
        </Button>
      </CardActionArea>
    </Card>
  );
};

export default GithubAd;
