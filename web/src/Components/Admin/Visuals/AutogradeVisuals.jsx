import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';

import AssignmentTestsPaper from './AssignmentTestsPaper';


export default function AutogradeVisuals({assignmentId}) {
  const {enqueueSnackbar} = useSnackbar();
  const [assignmentData, setAssignmentData] = React.useState([]);

  React.useEffect(() => {
    axios.get(`/api/admin/visuals/assignment/${assignmentId}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.assignment_data) {
        setAssignmentData(data.assignment_data);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <div style={{display: 'flex', justifyContent: 'center'}}>
      {assignmentData.map(({title, pass_time_scatter, pass_count_radial}) => (
        <AssignmentTestsPaper
          key={title}
          title={title}
          pass_time_scatter={pass_time_scatter}
          pass_count_radial={pass_count_radial}
        />
      ))}
    </div>
  );
}
