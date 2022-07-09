import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@mui/material/styles/makeStyles';
import Card from '@mui/material/Card';
import CardActionArea from '@mui/material/CardActionArea';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import SaveIcon from '@mui/icons-material/Save';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';

import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';

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

export default function UserCard({user, setUser, age}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [edits, setEdits] = useState(0);

  const incEdits = () => {
    setEdits((state) => ++state);
  };

  return (
    <Card className={classes.root}>
      <CardContent>
        <Grid container spacing={1} justify={'center'} alignItems={'flex-start'}>
          {/* netid */}
          <Grid item xs={12}>
            <Typography gutterBottom variant="subtitle1">
                Netid: {user.netid}
            </Typography>
            <Typography gutterBottom variant="subtitle2" style={{color: 'grey'}}>
                Account Age: {age}
            </Typography>
            <Typography gutterBottom variant="subtitle2" style={{color: 'grey'}}>
                Joined Platform: {user.created}
            </Typography>
          </Grid>

          {/* name */}
          <Grid item xs={12} md={6}>
            <TextField
              className={classes.textField}
              label="name"
              value={user.name}
              onChange={(e) => {
                setUser((state) => {
                  state.name = e.target.value;
                  return state;
                });
                incEdits();
              }}
            />
          </Grid>

          {/* github username */}
          <Grid item xs={12} md={6}>
            <TextField
              className={classes.textField}
              label="Github username"
              value={user.github_username}
              onChange={(e) => {
                setUser((state) => {
                  state.github_username = e.target.value;
                  return state;
                });
                incEdits();
              }}
            />
          </Grid>

        </Grid>
      </CardContent>

      <CardActionArea>
        <CardActions>
          <Button
            variant="contained"
            color="primary"
            size="small"
            startIcon={<SaveIcon/>}
            onClick={() => saveUser(user, enqueueSnackbar)}
          >
          Save
          </Button>
        </CardActions>
      </CardActionArea>
    </Card>
  );
}
