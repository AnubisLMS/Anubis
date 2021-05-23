import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import SaveIcon from '@material-ui/icons/Save';
import Switch from '@material-ui/core/Switch';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';

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
  const [edits, setEdits] = useState(0);

  const incEdits = () => {
    setEdits((state) => ++state);
  };

  return (
    <Card className={classes.root}>
      <CardActionArea>
        <CardContent>
          <Grid container spacing={1} justify={'center'} alignItems={'flex-start'}>
            {/* netid */}
            <Grid item xs={12}>
              <Typography gutterBottom variant="subtitle1">
                Netid: {user.netid}
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

            {/* Is Superuser */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={user.is_superuser}
                    color={'primary'}
                    onChange={() => {
                      axios.get(`/api/admin/students/toggle-superuser/${user.student.id}`).then((response) => {
                        const data = standardStatusHandler(response, enqueueSnackbar);
                        if (data) {
                          setUser((state) => {
                            state.is_superuser = !state.is_superuser;
                            return state;
                          });
                          incEdits();
                        }
                      }).catch(standardErrorHandler(enqueueSnackbar));
                    }}
                  />
                }
                label="Is Superuser"
                labelPlacement="end"
              />
            </Grid>
          </Grid>
        </CardContent>
      </CardActionArea>
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
    </Card>
  );
}
