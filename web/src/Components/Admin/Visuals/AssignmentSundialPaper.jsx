import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import useQuery from '../../../hooks/useQuery';
import Paper from '@material-ui/core/Paper';
import AssignmentSundial from './Graphs/AssignmentSundial';

const useStyles = makeStyles((theme) => ({
  root: {
    flex: 1,
  },
}));

export default function AssignmentSundialPaper() {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [sundialData, setSundialData] = useState([]);

  const assignmentId = query.get('assignmentId');

  React.useEffect(() => {
    axios.get(`/api/admin/visuals/sundial/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.sundial) {
        setSundialData(data?.sundial);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <Paper>
      <AssignmentSundial sundialData={sundialData} />
    </Paper>
  );
}
