import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Autocomplete from '@material-ui/lab/Autocomplete';

import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {TextField, Tooltip} from '@material-ui/core';
import AddIcon from '@material-ui/icons/Add';
import Fab from '@material-ui/core/Fab';
import Button from '@material-ui/core/Button';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';


const useStyles = makeStyles((theme) => ({
  fab: {
    margin: theme.spacing(1, 1),
  },
  autocomplete: {
    width: 150,
  },
  paper: {
    display: 'flex',
    padding: theme.spacing(1),
  },
  dataGridPaper: {
    padding: theme.spacing(1),
    height: 700,
  },
  inline: {
    display: 'inline',
  },
}));


export default function CourseTasProfessors({base}) {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [tas, setTas] = useState([]);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get(`/api/admin/courses/list/${base}s`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.users) {
        setTas(data.users);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  React.useEffect(() => {
    axios.get(`/api/admin/students/list/basic`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.users) {
        setUsers(data.users);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);


  const makeTA = () => {
    if (!selected) {
      enqueueSnackbar('select netid', {variant: 'error'});
      return;
    }
    axios.get(`/api/admin/courses/make/${base}/${selected.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const removeTA = (id) => () => {
    axios.get(`/api/admin/courses/remove/${base}/${id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setReset((prev) => ++prev);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const columns = [
    {field: 'id', headerName: 'ID', hide: true},
    {field: 'netid', headerName: 'Netid', width: 200},
    {field: 'name', headerName: 'Name', width: 200},
    {
      field: 'delete', headerName: 'Delete', width: 150, renderCell: (params) => (
        <Button
          variant={'contained'}
          color={'secondary'}
          startIcon={<DeleteForeverIcon/>}
          onClick={removeTA(params.row.id)}
        >
          Remove
        </Button>
      ),
    },
  ];

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
      <Grid item>
        <Paper className={classes.paper}>
          <div>
            <Tooltip title={`Make ${selected?.netid} a ${base}`}>
              <Fab
                size={'small'}
                color={'primary'}
                className={classes.fab}
                onClick={makeTA}
              >
                <AddIcon/>
              </Fab>
            </Tooltip>
          </div>
          <Autocomplete
            className={classes.autocomplete}
            renderInput={(params) => <TextField {...params} variant={'outlined'}/>}
            value={selected}
            getOptionLabel={(option) => `${option.netid} ${option.name}`}
            onChange={(_, e) => setSelected(e)}
            options={users}
          />
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper className={classes.dataGridPaper}>
          <DataGrid columns={columns} rows={tas}/>
        </Paper>
      </Grid>
    </Grid>
  );
}
