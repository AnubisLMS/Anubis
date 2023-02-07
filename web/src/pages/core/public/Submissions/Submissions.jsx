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
import ListPagination from '../../../../components/shared/ListPagination/ListPagination';

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

        const ogRows = data.submissions.map(translateSubmission);

        const paginatedSubmissions = [];

        while (ogRows.length) {
          paginatedSubmissions.push(ogRows.splice(0, 10));
        }
        setRows(paginatedSubmissions);
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
      {rows[page] && rows[0][0] && (
        <div>
          {rows[page].map((row, index) => (
            <div key={index}>
              {row?.tests && row?.commit &&
                <SubmissionItem
                  assignmentDue={row.assignmentDue}
                  assignmentName={row.assignment_name}
                  id={row.id}
                  commit={row.commit}
                  accepted={row.accepted}
                  processed={row.processed}
                  tests={row.tests}
                  timeStamp={row.timeStamp}
                />
              }
            </div>
          ))}
        </div>
      )}
      {/*
        Pagination has been added. However, we only want to load the results that correspond to each page
      */}
      {rows.length > 1 && (
        <ListPagination
          page = {page}
          maxPage = {rows.length}
          setPage = {(page) => setPage(page)}
          prevPage = {()=> setPage((page) => {
            if (page === 0) {
              return rows.length - 1;
            }
            return page - 1;
          })}
          nextPage = {() => setPage((page + 1) % rows.length)}
        />
      )}
    </StandardLayout>
  );
}
