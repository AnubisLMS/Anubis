import React, {useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import SubmissionItem from '../../../../components/core/SubmissionItem/SubmissionItem';
import useQuery from '../../../../hooks/useQuery';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import ListHeader from '../../../../components/shared/ListHeader/ListHeader';
import Divider from '../../../../components/shared/Divider/Divider';


function translateSubmission({id, assignment_name, assignment_due, commit, processed, state, created, tests}) {
  return {
    assignment_name, assignment_due, commit, created, tests,
    id, assignmentDue: new Date(assignment_due), state: state,
    processed: processed, timeStamp: new Date(created),
  };
}

export default function Submissions() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [rows, setRows] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rowCount, setRowCount] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const assignmentId = query.get('assignmentId');
  const courseId = query.get('courseId');
  const userId = query.get('userId');

  React.useEffect(() => {
    setLoading(true);
    axios.get(`/api/public/submissions/`, {
      params: {
        assignmentId, courseId, userId,
        limit: pageSize,
        offset: page * pageSize,
      },
    }).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.total) {
        setRowCount(data?.total);
      }
      if (data?.submissions) {
        let prev;
        if (rows.length === 0) {
          prev = new Array(data?.total);
          for (let i = 0; i < prev.length; ++i) {
            prev[i] = {id: i};
          }
        } else {
          prev = rows;
        }

        const translation = data.submissions.map(translateSubmission);
        for (let i = page * pageSize; i < (page * pageSize) + translation.length; ++i) {
          prev[i] = translation[i - (page * pageSize)];
        }

        setRows([...prev]);
      }
      if (data?.user) {
        setUser(data.user);
      }
      setLoading(false);
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, [pageSize, page]);

  return (
    <StandardLayout>
      <SectionHeader title='Submissions' isPage/>
      <Divider/>
      <ListHeader sections={['Assignment Name', 'Autograde Results', 'Submission', 'Submission Time']}/>
      {rows.map((row, index) => (
        <div key={index}>
          {row?.tests && row?.commit &&
            <SubmissionItem
              assignmentDue={row.assignmentDue}
              assignmentName={row.assignment_name}
              commit={row.commit}
              processed={row.processed}
              tests={row.tests}
              timeStamp={row.timeStamp}
            />
          }
        </div>
      ))}
    </StandardLayout>

  );
}
