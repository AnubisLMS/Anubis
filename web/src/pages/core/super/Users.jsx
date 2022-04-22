import React, {useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Input from '@material-ui/core/Input';

import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';

import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import SuperUserItem from '../../../components/core/UserItem/SuperUserItem';
import ListHeader from '../../../components/shared/ListHeader/ListHeader';
import ListPagination from '../../../components/shared/ListPagination/ListPagination.jsx';
import SectionHeader from '../../../components/shared/SectionHeader/SectionHeader';
import Divider from '../../../components/shared/Divider/Divider';

const useStyles = makeStyles((theme) => ({
  paper: {
    flex: 1,
    padding: theme.spacing(1),
  },
  studentList: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  dataGridPaper: {
    height: 800,
  },
  dataGrid: {
    height: '100%',
    display: 'flex',
  },
  autocomplete: {
    paddingBottom: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
  },
  search: {
    width: '100%',
    backgroundColor: theme.palette.dark.blue['100'],
    border: `1px solid ${theme.palette.dark.blue['200']}`,
    padding: theme.spacing(2),
    borderRadius: theme.spacing(1),
    marginTop: theme.spacing(2),
  },
}));


export default function Users() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [students, setStudents] = useState([]);
  const [page, setPage] = useState(0);

  const [refresh, setRefresh] = useState(0);

  const [searchQuery, setSearchQuery] = useState(undefined);

  const toggleSuperuser = (id, enqueueSnackbar) => () => {
    axios.get(`/api/admin/students/toggle-superuser/${id}`).then((response) => {
      if (standardStatusHandler(response, enqueueSnackbar)) {
        for (const student of students) {
          if (student.id === id) {
            student.is_superuser = !student.is_superuser;
          }
        }
        setRefresh((state) => ++state);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  React.useEffect(() => {
    axios.get('/api/super/students/list').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.students) {
        for (const student of data.students) {
          student.search = student.name.toLowerCase() +
            student.netid.toLowerCase() +
            (student.github_username ?? '').toString() +
            student.id.toLowerCase();
        }

        const students = [];
        while (data.students.length) {
          students.push(data.students.splice(0, 10));
        }

        setStudents(students);
      } else {
        enqueueSnackbar('Unable to fetch students', {variant: 'error'});
      }
    }).catch((error) => {
      enqueueSnackbar(error.toString(), {variant: 'error'});
    });
  }, [refresh]);

  React.useEffect(() => {
    if (searchQuery === '' || searchQuery === undefined) {
      setRefresh(refresh + 1);
      return;
    }
    const newStudents = students.flat(Infinity).filter((student) =>
      student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.netid.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (!!student.github_username && student.github_username.toLowerCase().includes(searchQuery.toLowerCase())),
    );

    const paginatedStudents = [];

    while (newStudents.length) {
      paginatedStudents.push(newStudents.splice(0, 10));
    }
    setStudents(paginatedStudents);
    setPage(0);
  }, [searchQuery]);

  return (
    <StandardLayout>
      <SectionHeader isPage title={'Users'} />
      <Divider />
      <Input
        placeholder={'Search Student By NetId, Name or Github Username'}
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value)}
        className={classes.search}
      >
      </Input>
      <ListHeader sections={['Name', 'Log-in as', 'Github Username', 'netid', 'View', 'Set Superuser']} />
      {students[page] && students[0][0] && (
        <div className={classes.studentList}>
          {(students[0].length > 1) ? students[page].map((student, index) => (
            <SuperUserItem
              key={`${student.netid}-${index}`}
              student={student}
              githubUsername={student.github_username}
              id={student.id}
              netid={student.netid}
              name={student.name}
              logIn={() => {
                axios.get(`/api/admin/auth/token/${student.netid}`).then((response) => {
                  const data = standardStatusHandler(response);
                  if (data) {
                    window.location.reload();
                  }
                }).catch(standardErrorHandler(enqueueSnackbar));
              }}
              superuser={toggleSuperuser(student.id, enqueueSnackbar)}
            />
          )) : (
            <SuperUserItem
              key={`${students[0][0].netid}`}
              githubUsername={students[0][0].github_username}
              id={students[0][0].id}
              netid={students[0][0].netid}
              name={students[0][0].name}
              logIn={() => {
                axios.get(`/api/admin/auth/token/${student.netid}`).then((response) => {
                  const data = standardStatusHandler(response);
                  if (data) {
                    window.location.reload();
                  }
                }).catch(standardErrorHandler(enqueueSnackbar));
              }}
              superuser={toggleSuperuser(student.id, enqueueSnackbar)}
            />
          )}
        </div>
      )}
      {students.length > 1 && (
        <ListPagination
          page={page}
          maxPage={students.length}
          setPage={(page) => setPage(page)}
          prevPage={() => setPage(page - 1)}
          nextPage={() => setPage(page + 1)}
        />
      )}
    </StandardLayout>
  );
}
