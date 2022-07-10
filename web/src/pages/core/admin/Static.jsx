import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';

import FileUploadDialog from '../../../components/core/Static/FileUploadDialog';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    padding: theme.spacing(1),
  },
  button: {
    margin: theme.spacing(1),
  },
}));

const deleteFile = (id, state, enqueueSnackbar) => () => {
  axios.get(`/api/admin/static/delete/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      state.setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};


const useColumns = (state, enqueueSnackbar) => ([
  {
    field: 'a', headerName: 'URL', width: 300, renderCell: ({row}) => (
      <div>
        <Typography
          variant={'body1'}
          color={'primary'}
          style={{display: 'inline'}}
          component={'a'}
          target={'_blank'}
          href={`${window.location.origin}/api/public/static${row.path}/${row.filename}`}
        >
          {row.filename}
        </Typography>
      </div>
    ),
  },
  {field: 'content_type', headerName: 'content Type', width: 150},
  {
    field: 'kill', headerName: 'Delete', width: 150, renderCell: ({row}) => (
      <Button
        variant={'contained'}
        color={'error'}
        size={'small'}
        startIcon={<DeleteForeverIcon/>}
        onClick={deleteFile(row.id, state, enqueueSnackbar)}
      >
        Delete File
      </Button>
    ),
  },
]);


export default function Static() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [files, setFiles] = useState([]);
  const [rows, setRows] = useState([]);
  const [reset, setReset] = useState([]);

  const pageState = {
    page, setPage,
    pageSize, setPageSize,
    files, setFiles,
    rows, setRows,
    reset, setReset,
  };

  React.useEffect(() => {
    axios.get('/api/admin/static/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setFiles(data.files);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [page, pageSize, reset]);

  React.useEffect(() => {
    setRows(files);
  }, [files]);

  const columns = useColumns(pageState, enqueueSnackbar);

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justifyContent={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Static File Management
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <FileUploadDialog className={classes.button} setReset={setReset}/>
        </Grid>
        <Grid item/>
        <Grid item xs={12} md={12} lg={10}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                <div style={{height: 700}}>
                  <DataGrid
                    pagination
                    page={page}
                    pageSize={pageSize}
                    rowsPerPageOptions={[10, 20, 30]}
                    onPageChange={(value) => setPage(value.page)}
                    onPageSizeChange={(value) => setPageSize(value.pageSize)}
                    className={classes.dataGrid}
                    columns={columns}
                    rows={rows}
                  />
                </div>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
}
