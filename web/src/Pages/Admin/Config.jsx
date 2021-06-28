import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';

import SaveIcon from '@material-ui/icons/Save';
import EditIcon from '@material-ui/icons/Edit';
import AddIcon from '@material-ui/icons/Add';

import {CustomGrid} from '../../Components/Shared';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    padding: theme.spacing(1),
    height: 400,
  },
}));


const saveConfig = (config, enqueueSnackbar) => {
  axios.post('/api/admin/config/save', {config}).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const updateRow = (index, item, setConfig) => (e) => {
  setConfig((prev) => {
    prev[index][item] = e.target.value;
    return [...prev];
  });
};

const updateAction = (index, setConfig, enqueueSnackbar) => () => {
  setConfig((prev) => {
    const action = prev[index]['action'];
    prev[index]['action'] = (
      action === 'edit' ? 'disabled' : 'edit'
    );
    if (prev[index]['action'] === 'disabled') {
      saveConfig(prev, enqueueSnackbar);
    }
    return [...prev];
  });
};

const useColumns = (config, setConfig, enqueueSnackbar) => ([
  {
    field: 'key',
    headerName: 'Key',
    width: 150,
    renderCell: (params) => (
      <TextField
        disabled={params.row.action === 'disabled'}
        value={params.row.key}
        onChange={updateRow(params.rowIndex, 'key', setConfig)}
      />
    ),
  },
  {
    field: 'value',
    headerName: 'Value',
    width: 250,
    renderCell: (params) => (
      <TextField
        disabled={params.row.action === 'disabled'}
        value={params.row.value}
        onChange={updateRow(params.rowIndex, 'value', setConfig)}
      />
    ),
  },
  {
    field: 'action',
    headerName: 'Edit',
    width: 200,
    renderCell: (params) => (
      <Button
        color={'primary'}
        variant={'contained'}
        size={'small'}
        onClick={updateAction(params.rowIndex, setConfig, enqueueSnackbar)}
        startIcon={params.row.action === 'edit' ? <SaveIcon/> : <EditIcon/>}
      >
        {params.row.action === 'edit' ? 'Save' : 'Edit'}
      </Button>
    ),
  },
]);

export default function Config() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [config, setConfig] = useState([]);
  const columns = useColumns(config, setConfig, enqueueSnackbar);

  React.useEffect(() => {
    axios.get('/api/admin/config/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setConfig(data.config.map(
          ({key, value}) => ({id: key, key, value, action: 'disabled'}),
        ));
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const addItem = () => {
    setConfig((prev) => {
      prev.push({
        id: `id${prev.length}`,
        key: 'key',
        value: 'value',
        action: 'edit',
      });
      return [...prev];
    });
  };

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justify={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Config
          </Typography>
        </Grid>
        <Grid item xs>
          <Button
            variant={'contained'}
            color={'primary'}
            onClick={addItem}
            startIcon={<AddIcon/>}
          >
            Add Item
          </Button>
        </Grid>
        <Grid item xs={12}>
          <CustomGrid {... {rows: config, columns: columns}} />
        </Grid>
      </Grid>
    </div>
  );
}
