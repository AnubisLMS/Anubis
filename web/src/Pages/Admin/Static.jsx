import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@material-ui/data-grid';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';

import {CustomGrid, PageTitle} from '../../Components/Shared';
import FileUploadDialog from '../../Components/Admin/Static/FileUploadDialog';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';

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
  {field: 'content_type', headerName: 'Content Type', width: 150},
  {
    field: 'kill', headerName: 'Delete', width: 150, renderCell: ({row}) => (
      <Button
        variant={'contained'}
        color={'secondary'}
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
      <Grid container spacing={4} justify={'center'} alignItems={'center'}>
        <PageTitle {... {description: 'Static File Management'}} />
        <Grid item xs={12}>
          <FileUploadDialog className={classes.button} setReset={setReset}/>
        </Grid>
        <Grid item/>
        <Grid item xs={12} md={12} lg={10}>
          <CustomGrid {... {columns: columns, rows: rows}} />
        </Grid>
      </Grid>
    </div>
  );
}
