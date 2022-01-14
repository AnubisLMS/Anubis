import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';
import {useParams} from 'react-router-dom';

import Paper from '@material-ui/core/Paper';

import useQuery from '../../../hooks/useQuery';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import AssignmentSundial from './Graphs/AssignmentSundial';


export default function AssignmentSundialPaper() {
  const params = useParams();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [sundialData, setSundialData] = useState([]);

  const assignmentId = query.get('assignmentId') ?? params.assignmentId;

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
