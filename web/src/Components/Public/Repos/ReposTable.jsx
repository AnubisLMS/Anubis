import React from 'react';

import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import makeStyles from '@material-ui/core/styles/makeStyles';

import IconButton from '@material-ui/core/IconButton';
import GitHubIcon from '@material-ui/icons/GitHub';

import AuthContext from '../../../Contexts/AuthContext';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));

const columns = [
  {field: 'course_code', headerName: 'Course', width: 150},
  {field: 'assignment_name', headerName: 'Assignment Name', width: 200},
  {field: 'github_username', headerName: 'Github Username', width: 200},
  {
    field: 'repo_url', headerName: 'Repo', width: 170, renderCell: ({row}) => (
      <IconButton
        color={'primary'}
        component={'a'}
        target={'_blank'}
        rel={'noreferrer'}
        href={row.repo_url}
      >
        <GitHubIcon/>
      </IconButton>
    ),
  },
];

export default function ReposTable({rows}) {
  const classes = useStyles();

  return (
    <div>
      <Paper className={classes.paper}>
        <DataGrid columns={columns} rows={rows}/>
      </Paper>
    </div>
  );
}
