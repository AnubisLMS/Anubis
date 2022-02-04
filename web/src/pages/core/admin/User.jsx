import React, {useState} from 'react';

import Grid from '@material-ui/core/Grid';
import {DataGrid} from '@material-ui/data-grid';

import useQuery from '../../../hooks/useQuery';
import UserCard from '../../../components/core/Users/UserCard';
import CourseCard from '../../../components/core/Users/CourseCard';
import axios from 'axios';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import {useSnackbar} from 'notistack';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import IconButton from '@material-ui/core/IconButton';
import CheckIcon from '@material-ui/icons/Check';
import CancelIcon from '@material-ui/icons/Cancel';
import GitHubIcon from '@material-ui/icons/GitHub';


export default function User() {
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [repos, setRepos] = useState([]);
  const [theia, setTheia] = useState([]);
  const [user, setUser] = useState(null);

  React.useEffect(() => {
    axios.get(`/api/admin/students/info/${query.get('userId')}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.user) {
        setUser(data.user);
      }
      if (data?.courses) {
        setCourses(data.courses);
      }
      if (data?.repos) {
        setRepos(data.repos);
      }
      if (data?.theia) {
        setTheia(data.theia);
      }
    });
  }, []);

  if (!user) {
    return null;
  }

  return (
    <Grid container spacing={4} justify={'center'} alignItems={'flex-start'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Student Management
        </Typography>
      </Grid>

      <Grid item xs={10}>
        <Grid container spacing={2}>

          {/* Student */}
          <Grid item xs={12} sm={6} md={4} key={'user-card'}>
            <Typography variant={'subtitle1'} color={'textSecondary'}>
              Student
            </Typography>
            <UserCard user={user} setUser={setUser}/>
          </Grid>

          {/* Courses */}
          <Grid item xs={12}>
            <Typography variant={'subtitle1'} color={'textSecondary'}>
              Courses
            </Typography>
            <Grid container spacing={2}>
              {courses.map((course) => (
                <Grid item xs={12} md={6} key={course?.id}>
                  <CourseCard user={user} course={course}/>
                </Grid>
              ))}
            </Grid>
          </Grid>

          {/* Repos */}
          <Grid item xs={12}>
            <Typography variant={'subtitle1'} color={'textSecondary'}>
              Repos
            </Typography>
            <Paper style={{height: 300}}>
              <DataGrid
                columns={[
                  {
                    field: 'repo_url', headerName: 'Repo URL', width: 500, renderCell: (params) => (
                      <a
                        href={params.row?.repo_url}
                        target={'_blank'}
                        rel={'noreferrer'}
                      >
                        {params.row?.repo_url}
                      </a>
                    ),
                  },
                  {field: 'assignment_name', headerName: 'Assignment', width: 200},
                  {field: 'course_code', headerName: 'Course Code', width: 150},
                ]}
                rows={repos}
              />
            </Paper>
          </Grid>

          {/* Theia */}
          <Grid item xs={12}>
            <Typography variant={'subtitle1'} color={'textSecondary'}>
              Recent IDEs
            </Typography>
            <Paper style={{height: 300}}>
              <DataGrid
                columns={[
                  {
                    field: 'playground', headerName: 'Playground', width: 120, renderCell: (params) => (
                      <IconButton color={params.value ? 'primary' : 'secondary'}>
                        {params.value ? <CheckIcon/> : <CancelIcon/>}
                      </IconButton>
                    ),
                  },
                  {
                    field: 'image', headerName: 'Image', width: 100, renderCell: (params) => (params.value.title),
                  },
                  {
                    field: 'image_tag', headerName: 'Image Tag', width: 120, renderCell: (params) => (
                      params.value || params.row.image.default_tag || 'latest'
                    ),
                  },
                  {field: 'created', headerName: 'Start Time', width: 170},
                  {field: 'ended', headerName: 'End Time', width: 170},
                  {field: 'state', headerName: 'State'},
                  {
                    field: 'autosave', headerName: 'Autosave', width: 120, renderCell: (params) => (
                      <IconButton color={params.row.autosave ? 'primary' : 'secondary'}>
                        {params.row.autosave ? <CheckIcon/> : <CancelIcon/>}
                      </IconButton>
                    ),
                  },
                  {
                    field: 'repo_url', headerName: 'Repo', width: 100, renderCell: ({row}) => (
                      <IconButton color={'primary'} component={'a'} href={row.repo_url} target={'_blank'}>
                        <GitHubIcon/>
                      </IconButton>
                    ),
                  },
                  {field: 'assignment_name', headerName: 'Assignment', width: 150},
                  {field: 'course_code', headerName: 'Course Code', width: 150},
                ]}
                rows={theia}
              />
            </Paper>
          </Grid>

        </Grid>
      </Grid>
    </Grid>
  );
}
