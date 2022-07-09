import React from 'react';
import {useHistory} from 'react-router-dom';

import GitHubIcon from '@mui/icons-material/GitHub';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import {useStyles} from './RepoItem.styles';
import Item from '../../shared/Item/Item';

const RepoItem = ({
  assignmentId,
  assignmentName,
  courseCode,
  ready,
  repo_url,
  openDialog,
}) => {
  const classes = useStyles();

  return (
    <Item
      showStatus={false}
      title={assignmentName}
      subTitle={courseCode}
      titleIcon={<GitHubIcon />}
    >
      <Typography>{courseCode}</Typography>
      <Typography>{ready ? 'Ready' : 'Processing'}</Typography>
      <Box className={classes.actionsContainer}>
        <Button
          variant={'contained'}
          color={'secondary'}
          className={classes.deleteButton}
          onClick={() => openDialog(assignmentId)}
        >
          Delete Repo
        </Button>
        <Button
          component="a"
          variant={'contained'}
          color={'primary'}
          href={repo_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          View Repo
        </Button>
      </Box>

    </Item>
  );
};

export default RepoItem;
