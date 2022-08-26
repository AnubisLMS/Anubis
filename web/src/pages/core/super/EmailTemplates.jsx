import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {DataGrid} from '@mui/x-data-grid';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';

import SaveIcon from '@mui/icons-material/Save';
import DeleteForever from '@mui/icons-material/DeleteForever';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';

import AceEditor from 'react-ace';
import 'ace-builds/src-min-noconflict/mode-text';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import makeStyles from '@mui/styles/makeStyles';


const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
  paper: {
    padding: theme.spacing(1),
    height: 700,
  },
  button: {
    padding: theme.spacing(1),
  },
  tagsModel: {
    minWidth: 1024,
  },
}));


export default function EmailTemplates() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [editOpen, setEditOpen] = useState(null);
  const [newKey, setNewKey] = useState('');
  const [templates, setTemplates] = useState([]);

  const api = (method, url = `/api/super/email/template/list`, config = {}) => {
    method(url, config).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.templates) {
        setTemplates(data.templates);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  useEffect(() => {
    api(axios.get);
  }, []);

  const addTemplate = (key) => {
    api(axios.post, `/api/super/email/template/new`, {key});
  };
  const delTemplate = (key) => {
    api(axios.post, `/api/super/email/template/delete`, {key});
  };
  const saveTemplate = (template) => {
    api(axios.post, `/api/super/email/template/save`, template);
  };

  const columns = [
    {field: 'key', width: 300},
    {field: 'subject', width: 300},
    {
      field: 'edit', width: 120, renderCell: (params) => (
        <Button
          startIcon={<EditIcon/>}
          variant={'contained'}
          color={'primary'}
          size={'small'}
          onClick={() => setEditOpen(params.row)}
        >
          Edit
        </Button>
      ),
    },
    {
      field: 'del', width: 120, renderCell: (params) => (
        <Button
          startIcon={<DeleteForever/>}
          variant={'contained'}
          color={'error'}
          size={'small'}
          onClick={() => delTemplate(params.row.key)}
        >
          Delete
        </Button>
      ),
    },
  ];

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Email Templates
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
          }}>
            <Button
              variant={'contained'}
              color={'primary'}
              onClick={() => addTemplate(newKey)}
              startIcon={<AddIcon/>}
            >
              Add Template
            </Button>
            <TextField
              variant={'outlined'}
              label={'key'}
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
            />
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Dialog
            open={!!editOpen}
            onClose={() => {
                saveTemplate(editOpen);
                setEditOpen(false);
            }}
          >
            <DialogTitle>{editOpen?.key}</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{mt: 0.5}}>

                <Grid item xs={12}>
                  <Typography variant={'subtitle1'}>
                    Subject:
                  </Typography>
                  <AceEditor
                    mode="text"
                    theme="monokai"
                    height={50}
                    value={editOpen?.subject}
                    onChange={(v) => setEditOpen((prev) => {
                      prev.subject = v;
                      return {...prev};
                    })}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Typography variant={'subtitle1'}>
                    Body:
                  </Typography>
                  <AceEditor
                    mode="text"
                    theme="monokai"
                    value={editOpen?.body}
                    onChange={(v) => setEditOpen((prev) => {
                      prev.body = v;
                      return {...prev};
                    })}
                  />
                </Grid>

              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                saveTemplate(editOpen);
                setEditOpen(false);
              }} color="primary" variant="contained">
                Close
              </Button>
            </DialogActions>
          </Dialog>

          <Paper className={classes.paper}>
            <DataGrid
              rows={templates}
              columns={columns}
              pageSize={10}
              getRowId={(item) => item.key}
            />
          </Paper>
        </Grid>

      </Grid>
    </div>
  );
}

