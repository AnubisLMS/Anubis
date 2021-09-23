import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@material-ui/data-grid';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';

import {useStyles} from './Lectures.styles';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import useQuery from '../../../hooks/useQuery';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import Typography from '@material-ui/core/Typography';

const Lectures = () => {
  const classes = useStyles();
  const query = useQuery();
  const {enqueueSnackbar} = useSnackbar();
  const [lectures, setLectures] = useState([]);

  const courseId = query.get('courseId') ?? '';

  useEffect(() => {
    axios.get(`/api/public/lectures/list`, {params: {courseId}}).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data.lectures) {
        setLectures(data.lectures);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const get_href = (row) => (
    `${window.location.origin}/api/public/static${row.static_file.path}/${row.static_file.filename}`
  );

  return (
    <StandardLayout title={'Lectures'} description={'Lecture notes posted by professors'}>
      <Grid container spacing={1} justify={'center'}>
        <Grid item xs={12}>
          <Paper className={classes.paper}>
            <DataGrid
              columns={[
                {field: 'course', headerName: 'Course', width: 150},
                {field: 'post_time', headerName: 'Post Time', width: 170},
                {field: 'title', headerName: 'Title', width: 300},
                {
                  field: 'a', headerName: 'Lecture Attachment', width: 300, renderCell: ({row}) => (
                    <div>
                      <Typography
                        variant={'body1'}
                        color={'primary'}
                        style={{display: 'inline'}}
                        component={'a'}
                        target={'_blank'}
                        href={get_href(row)}
                      >
                        {row.static_file.filename}
                      </Typography>
                    </div>
                  ),
                },
              ]}
              rows={lectures}
              rowsPerPageOptions={[10, 20, 30]}
              pagination
            />
          </Paper>
        </Grid>
      </Grid>
    </StandardLayout>
  );
};

export default Lectures;
