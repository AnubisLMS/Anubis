import React from 'react';

import {useStyles} from './Ad.styles';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import GitHubIcon from '@material-ui/icons/GitHub';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';

const Ad = () => {
  const classes = useStyles();

  return (
    <Card className={classes.root}>
      <CardActionArea
        className={classes.actionArea}
        href="https://github.com/AnubisLMS/Anubis"
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
        <Button className={classes.githubButton}>
          {'We\'re on Github'}
        </Button>
      </CardActionArea>
    </Card>
  );
};

export default Ad;
