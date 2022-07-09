import React from 'react';
import {useHistory} from 'react-router-dom';

import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

import {useStyles} from './SectionHeader.styles';

const SectionHeader = ({
  title,
  link,
  linkText,
  isPage = false,
}) => {
  const classes = useStyles();
  const history = useHistory();

  return (
    <Box className={classes.root}>
      <Typography className={isPage ? classes.pageTitle : classes.title}>{title}</Typography>
      {link && (
        <Button
          className={classes.button}
          onClick={() => history.push(link)}
        >
          {linkText}
        </Button>
      )}
    </Box>
  );
};

export default SectionHeader;

