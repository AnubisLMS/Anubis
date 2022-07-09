import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Box from '@mui/material/Box';
import makeStyles from '@mui/styles/makeStyles';

import useQuery from '../../../hooks/useQuery';
import AssignmentItem from '../../../components/core/AssignmentItem/AssignmentItem';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import IDEDialog from '../../../components/core/IDE/IDEDialog';
import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../components/shared/SectionHeader/SectionHeader';
import ListHeader from '../../../components/shared/ListHeader/ListHeader';
import Divider from '../../../components/shared/Divider/Divider';


const Assignments = () => {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [assignments, setAssignments] = useState([]);
  const [selectedTheia, setSelectedTheia] = useState(null);
  const [runAssignmentPolling, setRunAssignmentPolling] = useState(false);
  const [pollingAssignmentId, setPollingAssignmentId] = useState(null);

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
    <StandardLayout>
      <IDEDialog selectedTheia={selectedTheia} setSelectedTheia={setSelectedTheia}/>
      <SectionHeader isPage title='Assignments' />
      <Divider />
      <ListHeader sections={['Assignment Name', 'Submitted', 'Due Date', 'Actions']} />
      {assignments && assignments.map((assignment, index) => (
        <AssignmentItem
          key={`${assignment.name}-${index}`}
          name={assignment.name}
          dueDate={assignment.due_date}
          id={assignment.id}
          course={assignment.course}
          submitted={assignment.has_submission}
          visible_to_students={assignment.visible_to_students}
        />
      ))}
    </StandardLayout>
  );
};

export default Assignments;
