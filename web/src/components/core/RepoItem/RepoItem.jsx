import React from 'react';
import {useHistory} from 'react-router-dom';

import GitHubIcon from '@material-ui/icons/GitHub';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';

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
