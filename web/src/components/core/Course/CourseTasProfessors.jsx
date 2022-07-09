import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Autocomplete from '@mui/lab/Autocomplete';
import Tooltip from '@mui/material/Tooltip';
import TextField from '@mui/material/TextField';
import Fab from '@mui/material/Fab';
import Button from '@mui/material/Button';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import AddIcon from '@mui/icons-material/Add';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';


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
    <Grid container spacing={2} justifyContent={'center'} alignItems={'center'}>
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
