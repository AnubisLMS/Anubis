import React, {useState} from 'react';

import {useSnackbar} from 'notistack';
import axios from 'axios';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import useQuery from '../../../hooks/useQuery';
import Paper from '@material-ui/core/Paper';
import AssignmentSundial from './Graphs/AssignmentSundial';
import {useParams} from 'react-router-dom';


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
