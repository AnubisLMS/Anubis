import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import Typography from '@material-ui/core/Typography';
import {DataGrid} from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import axios from 'axios';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import FileUploadDialog from '../../Components/Admin/Static/FileUploadDialog';

const useStyles = makeStyles((theme) => ({
  paper: {
    minHeight: 700,
    padding: theme.spacing(1),
  },
  // dataGrid: {
  //   height: '100%',
  // },
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
  {field: 'id', headerName: 'ID'},
  {field: 'content_type', headerName: 'Content Type', width: 150},
  {
    field: 'path', headerName: 'URL', width: 200, renderCell: ({row}) => (
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
