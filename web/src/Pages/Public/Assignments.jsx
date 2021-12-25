import React, {useState, useEffect} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import Box from '@material-ui/core/Box';
import makeStyles from '@material-ui/core/styles/makeStyles';

import useQuery from '../../Hooks/useQuery';
import AssignmentItem from '../../Components/Public/AssignmentItem/AssignmentItem';
import standardErrorHandler from '../../Utils/standardErrorHandler';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import IDEDialog from '../../Components/Public/IDE/IDEDialog';
import StandardLayout from '../../Components/Shared/Layouts/StandardLayout';
import SectionHeader from '../../Components/Shared/SectionHeader/SectionHeader';

const useStyles = makeStyles((theme) => ({
  divider: {
    width: '100%',
    borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
    marginTop: theme.spacing(2),
    height: '1px',
  },
}));

const Assignments = () => {
  const classes = useStyles();
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
      <Box className={classes.divider}/>
      {assignments && assignments.map((assignment, index) => (
        <AssignmentItem
          key={`${assignment.name}-${index}`}
          name={assignment.name}
          dueDate={assignment.due_date}
          id={assignment.id}
          course={assignment.course}
          submitted={assignment.has_submission}
        />
      ))}
    </StandardLayout>
  );
};

export default Assignments;
