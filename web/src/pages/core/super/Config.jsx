import React, {useState} from 'react';
import makeStyles from '@mui/styles/makeStyles';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';


import SaveIcon from '@mui/icons-material/Save';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';


import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import ReactAce from 'react-ace';

import 'ace-builds/src-noconflict/mode-java';
import 'ace-builds/src-noconflict/theme-github';
import 'ace-builds/src-noconflict/ext-language_tools';
import Box from '@mui/material/Box';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
}));


const saveConfig = (config, enqueueSnackbar) => {
  axios.post('/api/super/config/save', {config}).then((response) => {
    standardStatusHandler(response, enqueueSnackbar);
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const useColumns = (config, setConfig, setEdit) => ([
  {
    field: 'key',
    headerName: 'Key',
    width: 350,
  },
  {
    field: 'value',
    headerName: 'Value',
    width: 400,
  },
  {
    field: 'action',
    headerName: 'Edit',
    width: 100,
    renderCell: (params) => (
      <Button
        color={'primary'}
        variant={'contained'}
        size={'small'}
        onClick={() => setEdit(params.row)}
        startIcon={<EditIcon/>}
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
  const [edit, setEdit] = useState(null);

  const columns = useColumns(config, setConfig, setEdit, enqueueSnackbar);

  React.useEffect(() => {
    axios.get('/api/super/config/list').then((response) => {
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
      const newThing = new Array(...prev);
      newThing.push({
        id: `id${prev.length}`,
        key: 'key',
        value: 'value',
        action: 'edit',
      });
      return newThing;
    });
  };

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
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
          <Paper className={classes.paper}>
            <Dialog open={!!edit} onClose={() => setEdit(null)}>
              {edit && (
                <React.Fragment>
                  <DialogTitle>Edit {edit.key}</DialogTitle>
                  <DialogContent>
                    <TextField
                      autoFocus
                      margin="dense"
                      id="key"
                      label="Key"
                      fullWidth
                      variant="standard"
                      value={edit.key}
                      onChange={(e) => setEdit((prev) => {
                        prev.key = e.target.value;
                        return {...prev};
                      })}
                    />
                    <Box sx={{mt: 1}}>
                      <Typography>
                        Value
                      </Typography>
                      <ReactAce
                        mode="json"
                        theme="monokai"
                        value={edit.value}
                        maxLines={32}
                        minLines={12}
                        onChange={(v) => setEdit((prev) => {
                          prev.value = v;
                          return {...prev};
                        })}
                      />
                    </Box>
                  </DialogContent>
                  <DialogActions>
                    <Button
                      variant={'contained'}
                      color={'primary'}
                      onClick={() => setEdit(null)}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant={'contained'}
                      color={'primary'}
                      autoFocus
                      onClick={() => {
                        setEdit(null);
                        saveConfig(edit, enqueueSnackbar);
                      }}
                      startIcon={<SaveIcon/>}
                    >
                      Save
                    </Button>
                  </DialogActions>
                </React.Fragment>
              )}
            </Dialog>
            <DataGrid
              rows={config}
              columns={columns}
              pageSize={10}
            />
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}
