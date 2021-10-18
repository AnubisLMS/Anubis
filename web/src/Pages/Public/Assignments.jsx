import React, {useState, useEffect} from 'react';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import useQuery from '../../hooks/useQuery';

import AssignmentCardV2 from '../../Components/Public/Assignments/AssignmentCardV2/AssignmentCardV2';
import axios from 'axios';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import {useSnackbar} from 'notistack';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import IDEDialog from '../../Components/Public/IDE/IDEDialog';
import StandardLayout from '../../Components/Layouts/StandardLayout';


const Assignments = () => {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [selectedTheia, setSelectedTheia] = useState(null);
  const [runAssignmentPolling, setRunAssignmentPolling] = useState(false);
  const [pollingAssignmentId, setPollingAssignmentId] = useState(null);
  console.log(assignments);

  useEffect(() => {
    axios.get('/api/public/assignments', {params: {courseId: query.get('courseId')}}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setAssignments(data.assignments);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (runAssignmentPolling) {
      const endPollingTimeout = setTimeout(() => {
        setRunAssignmentPolling(false);
      }, 60_000);

      const runPollingInterval = setInterval(() => {
        axios.get(`/api/public/repos/get/${pollingAssignmentId}`).then((response) => {
          const data = standardStatusHandler(response, enqueueSnackbar);

          if (data.repo && data.repo.ready) {
            setAssignments((prev) => {
              for (const assignment of prev) {
                if (assignment.id === pollingAssignmentId) {
                  assignment.has_repo = true;
                  assignment.repo_url = data.repo.repo_url;
                }
              }
              return [...prev];
            });
            setRunAssignmentPolling(false);
          }
        }).catch(standardErrorHandler(enqueueSnackbar));
      }, 1_000);

      return () => {
        clearTimeout(endPollingTimeout);
        clearInterval(runPollingInterval);
      };
    }
  }, [runAssignmentPolling, setRunAssignmentPolling, pollingAssignmentId]);

  return (
    <StandardLayout
      title={'Anubis'}
      description={'Assignments'}
    >
      <IDEDialog selectedTheia={selectedTheia} setSelectedTheia={setSelectedTheia}/>
      <Grid container spacing={2}>
        {assignments.map((assignment, pos) => (
          <Grid item xs={12} sm={6} lg={4} key={assignment.id}>
            <Grow
              in={true}
              style={{transformOrigin: '0 0 0'}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <AssignmentCardV2 {... assignment}/>
            </Grow>
          </Grid>
        ))}
      </Grid>
    </StandardLayout>
  );
};

export default Assignments;
