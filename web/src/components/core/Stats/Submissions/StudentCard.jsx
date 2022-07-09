import React from 'react';
import {Link} from 'react-router-dom';

import makeStyles from '@mui/styles/makeStyles';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import ArchiveIcon from '@mui/icons-material/Archive';

const useStyles = makeStyles({
  root: {
    minWidth: 275,
  },
});


export default function StudentCard({student, assignment = null}) {
  const classes = useStyles();

  if (!student) {
    return null;
  }

  return (
    <Card className={classes.root}>
      <CardContent>
        <Typography variant={'h6'}>
          Student
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Name: {student.name}
        </Typography>
        <Typography color="textSecondary" gutterBottom>
          Netid: {student.netid}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          size="small"
          color={'primary'}
          variant={'contained'}
          component={Link}
          to={`/admin/user?userId=${student.id}`}
        >
          View Student
        </Button>
        {!!assignment && (
          <Button
            size={'small'}
            startIcon={<ArchiveIcon/>}
            color={'primary'}
            variant={'contained'}
            component={'a'}
            href={`/api/admin/questions/history/${assignment.id}/${student.id}`}
            download
          >
            Export Response History (json)
          </Button>
        )}
      </CardActions>
    </Card>
  );
}
