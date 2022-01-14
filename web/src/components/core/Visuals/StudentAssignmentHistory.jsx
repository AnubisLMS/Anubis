import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import useQuery from '../../../hooks/useQuery';
import StudentHistory from './Graphs/StudentHistory';


export default function StudentAssignmentHistory() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [testResults, setTestResults] = useState([]);
  const [buildResults, setBuildResults] = useState([]);

  const assignmentId = query.get('assignmentId');
  const netid = query.get('netid');

  React.useEffect(() => {
    axios.get(`/api/admin/visuals/history/${assignmentId}/${netid}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.submissions?.test_results) {
        setTestResults(data?.submissions.test_results);
      }
      if (data?.submissions?.build_results) {
        setBuildResults(data?.submissions.build_results);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <StudentHistory
      testResults={testResults}
      buildResults={buildResults}
    />
  );
}
