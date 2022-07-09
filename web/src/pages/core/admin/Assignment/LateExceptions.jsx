import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import {useParams} from 'react-router-dom';

import {DataGrid} from '@mui/x-data-grid';
import makeStyles from '@mui/material/styles/makeStyles';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Tooltip from '@mui/material/Tooltip';

import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import IconButton from '@mui/material/IconButton';

import standardErrorHandler from '../../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import LateExceptionAddCard from '../../../../components/core/Assignment/LateExceptionAddCard';

const useStyles = makeStyles((theme) => ({
  paper: {
    height: 700,
    padding: theme.spacing(1),
  },
}));

export default function LateExceptions() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const {assignmentId} = useParams();
  const [assignment, setAssignment] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [reset, setReset] = useState(0);

  React.useEffect(() => {
    axios.get(`/api/admin/late-exceptions/list/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignment) {
        setAssignment(data.assignment);
      }
      if (data?.late_exceptions) {
        setExceptions(data.late_exceptions.map((item) => {
          item.id = item.user_id;
          return item;
        }));
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [reset]);

  const remove = ({assignment_id, user_id}) => () => {
    axios.get(`/api/admin/late-exceptions/remove/${assignment_id}/${user_id}`).then((response) => {
      standardStatusHandler(response, enqueueSnackbar);
      setReset((prev) => ++prev);
    }).catch(standardErrorHandler(enqueueSnackbar));
  };


  if (assignment === null) {
    return <CircularProgress/>;
  }

  return (
    <Grid container spacing={2} justify={'center'} alignItems={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Late Exceptions for {assignment.name}
        </Typography>
      </Grid>
      <Grid item xs={6}>
        <LateExceptionAddCard assignment={assignment} setReset={setReset} />
      </Grid>
      <Grid item xs={12} md={10}>
        <Paper className={classes.paper}>
          <DataGrid columns={[
            {field: 'id', hide: true},
            {field: 'user_name', headerName: 'Name', width: 200},
            {field: 'user_netid', headerName: 'Netid', width: 100},
            {field: 'due_date', headerName: 'Due Date', width: 170},
            {field: 'delete', headerName: 'Delete', width: 170, renderCell: ({row}) => (
              <Tooltip title={'Delete late exception'}>
                <IconButton color={'secondary'} onClick={remove(row)}>
                  <DeleteForeverIcon/>
                </IconButton>
              </Tooltip>
            )},
          ]} rows={exceptions}/>
        </Paper>
      </Grid>
    </Grid>
  );
}
