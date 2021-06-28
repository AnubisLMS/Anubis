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
import EditIcon from '@material-ui/icons/Edit';

import LectureUploadDialog from '../../Components/Admin/Lecture/LectureUploadDialog';
import LectureEditDialog from '../../Components/Admin/Lecture/LectureEditDialog';
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
  axios.get(`/api/admin/lecture/delete/${id}`).then((response) => {
    const data = standardStatusHandler(response, enqueueSnackbar);
    if (data) {
      state.setReset((prev) => ++prev);
    }
  }).catch(standardErrorHandler(enqueueSnackbar));
};

const useColumns = (state, enqueueSnackbar) => ([
  {field: 'number', headerName: 'Lecture Number', width: 160},
  {field: 'title', headerName: 'Lecture Title', width: 300},
  {
    field: 'a', headerName: 'Lecture File', width: 300, renderCell: ({row}) => (
      <div>
        <Typography
          variant={'body1'}
          color={'primary'}
          style={{display: 'inline'}}
          component={'a'}
          target={'_blank'}
          href={`${window.location.origin}/api/public/static${row.static_file.path}/${row.static_file.filename}`}
        >
          {row.static_file.filename}
        </Typography>
      </div>
    ),
  },
  {
    field: 'edit', headerName: 'Edit', width: 150, renderCell: ({row}) => (
      <Button
        variant={'contained'}
        color={'primary'}
        size={'small'}
        startIcon={<EditIcon/>}
        onClick={() => state.setOpenEdit(row)}
      >
        Edit
      </Button>
    ),
  },
  {
    field: 'kill', headerName: 'Delete', width: 150, renderCell: ({row}) => (
      <Button
        variant={'contained'}
        color={'secondary'}
        size={'small'}
        startIcon={<DeleteForeverIcon/>}
        onClick={deleteFile(row, state, enqueueSnackbar)}
      >
        Delete
      </Button>
    ),
  },
]);


export default function Static() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [openEdit, setOpenEdit] = useState(null);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [lectures, setLectures] = useState([]);
  const [rows, setRows] = useState([]);
  const [reset, setReset] = useState([]);

  const pageState = {
    page, setPage,
    pageSize, setPageSize,
    lectures, setLectures,
    rows, setRows,
    reset, setReset,
    openEdit, setOpenEdit,
  };

  React.useEffect(() => {
    axios.get('/api/admin/lectures/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setLectures(data.lectures);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [page, pageSize, reset]);

  React.useEffect(() => {
    setRows(lectures);
  }, [lectures]);

  const columns = useColumns(pageState, enqueueSnackbar);

  return (
    <div className={classes.root}>
      <Grid container spacing={4} justify={'center'} alignItems={'center'}>
        <Grid item xs={12}>
          <Typography variant="h6">
            Anubis
          </Typography>
          <Typography variant={'subtitle1'} color={'textSecondary'}>
            Lecture Management
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <LectureUploadDialog className={classes.button} setReset={setReset}/>
          <LectureEditDialog
            lecture={openEdit}
            open={openEdit !== null}
            setOpen={setOpenEdit}
            className={classes.button}
            setReset={setReset}
          />
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
