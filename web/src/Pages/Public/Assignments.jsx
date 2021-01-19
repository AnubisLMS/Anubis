import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import useQuery from '../../hooks/useQuery';

import AssignmentCard from '../../Components/Public/Assignments/AssignmentCard';
import Typography from '@material-ui/core/Typography';
import axios from 'axios';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import {useSnackbar} from 'notistack';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import IDEDialog from '../../Components/Public/IDE/IDEDialog';


export default function AssignmentView() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [selectedTheia, setSelectedTheia] = useState(null);

  React.useEffect(() => {
    axios.get('/api/public/assignments/', {params: {courseId: query.get('courseId')}}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <Grid container spacing={4} justify={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Assignments
        </Typography>
      </Grid>
      <IDEDialog selectedTheia={selectedTheia} setSelectedTheia={setSelectedTheia}/>
      <Grid item/>
      <Grid item xs={12} md={10}>
        <Grid container spacing={4}>
          {assignments.map((assignment, pos) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={assignment.id}>
              <Grow
                in={true}
                style={{transformOrigin: '0 0 0'}}
                {...({timeout: 300 * (pos + 1)})}
              >
                <AssignmentCard assignment={assignment} setSelectedTheia={setSelectedTheia}/>
              </Grow>
            </Grid>
          ))}
        </Grid>
      </Grid>
    </Grid>
  );
}
