import React, {useState, useEffect} from 'react';

import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';
import useQuery from '../../hooks/useQuery';

import AssignmentCard from '../../Components/Public/Assignments/AssignmentCard';
import axios from 'axios';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import {useSnackbar} from 'notistack';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import IDEDialog from '../../Components/Public/IDE/IDEDialog';
import StandardLayout from '../../Components/Layouts/StandardLayout';


export default function AssignmentView() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [selectedTheia, setSelectedTheia] = useState(null);
  const [runAssignmentPolling, setRunAssignmentPolling] = useState(false);

  useEffect(() => {
    axios.get('/api/public/assignments/', {params: {courseId: query.get('courseId')}}).then((response) => {
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
        axios.get('/api/public/assignments/', {params: {courseId: query.get('courseId')}}).then((response) => {
          const data = standardStatusHandler(response, enqueueSnackbar);

          if (data) {
            // compare assignments to see if any have a corresponding repo now
            const assignmentsHasChanged = !assignments.every((assignment) => {
              const matchingResponseAssignment = data.assignments.find((a) => a.id === assignment.id);

              return assignment.has_repo === matchingResponseAssignment.has_repo;
            });

            if (assignmentsHasChanged) {
              setAssignments(data.assignments);
              setRunAssignmentPolling(false);
            }
          }
        }).catch(standardErrorHandler(enqueueSnackbar));
      }, 5_000);

      return () => {
        clearTimeout(endPollingTimeout);
        clearInterval(runPollingInterval);
      };
    }
  }, [runAssignmentPolling, setRunAssignmentPolling]);

  return (
    <StandardLayout
      title={'Anubis'}
      description={'Assignments'}
    >
      <IDEDialog selectedTheia={selectedTheia} setSelectedTheia={setSelectedTheia}/>
      <Grid container spacing={2}>
        {assignments.map((assignment, pos) => (
          <Grid item xs={12} sm={6} md={4} lg={4} key={assignment.id}>
            <Grow
              in={true}
              style={{transformOrigin: '0 0 0'}}
              {...({timeout: 300 * (pos + 1)})}
            >
              <AssignmentCard
                assignment={assignment}
                setSelectedTheia={setSelectedTheia}
                runAssignmentPolling={runAssignmentPolling}
                setRunAssignmentPolling={setRunAssignmentPolling} />
            </Grow>
          </Grid>
        ))}
      </Grid>
    </StandardLayout>
  );
}
