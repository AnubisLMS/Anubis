import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import SaveIcon from '@material-ui/icons/Save';
import {useSnackbar} from 'notistack';
import axios from 'axios';

const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 500,
  },
  textField: {
    margin: theme.spacing(1),
  },
}));

function saveUser(user, enqueueSnackbar) {
  axios.post(
    `/api/admin/students/update/${user.id}`,
    {name: user.name, github_username: user.github_username},
  ).then((response) => {
    if (response.data) {
      if (response.status === 200) {
        enqueueSnackbar(response.data.data.status, {variant: 'success'});
      } else {
        enqueueSnackbar(response.data.error, {variant: 'error'});
      }
    } else {
      enqueueSnackbar('unable to save', {variant: 'error'});
    }
  }).catch((error) => {
    enqueueSnackbar(error.toString(), {variant: 'error'});
  });
}

export default function UserCard({user, setUser}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();

  const {student} = user;

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardContent>
          {/* netid */}
          <Typography gutterBottom variant="subtitle1">
            {student.netid}
          </Typography>

          {/* name */}
          <TextField
            className={classes.textField}
            label="name"
            value={student.name}
            onChange={(e) => setUser(({student: {name, ...rest1}, ...rest2}) => ({
              student: {
                name: e.target.value,
                ...rest1,
              },
              ...rest2,
            }))}
          />

          {/* github username */}
          <TextField
            className={classes.textField}
            label="Github username"
            value={student.github_username}
            onChange={(e) => setUser(({student: {github_username, ...rest1}, ...rest2}) => ({
              student: {
                github_username: e.target.value,
                ...rest1,
              },
              ...rest2,
            }))}
          />
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button
          variant="contained"
          color="primary"
          size="small"
          startIcon={<SaveIcon/>}
          onClick={() => saveUser(student, enqueueSnackbar)}
        >
          Save
        </Button>
      </CardActions>
    </Card>
  );
}
