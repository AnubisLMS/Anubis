import React from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';

import AssignmentTestsPaper from './AssignmentTestsPaper';
import AssignmentSundialPaper from './AssignmentSundialPaper';
import Grid from '@material-ui/core/Grid';


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
    <Grid container spacing={1} justify={'center'} alignItems={'center'}>
      <Grid item>
        <AssignmentSundialPaper/>
      </Grid>
      {assignmentData.length !== 0 ? (
        <Grid item>
          <Grid container spacing={1} justify={'center'} alignItems={'center'}>
            {assignmentData.map(({title, pass_time_scatter, pass_count_radial}) => (
              <Grid item xs key={title}>
                <AssignmentTestsPaper
                  title={title}
                  pass_time_scatter={pass_time_scatter}
                  pass_count_radial={pass_count_radial}
                />
              </Grid>
            ))}
          </Grid>
        </Grid>
      ) : null}
    </Grid>
  );
}
