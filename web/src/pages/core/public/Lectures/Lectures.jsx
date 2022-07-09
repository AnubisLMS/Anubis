import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import {DataGrid} from '@mui/x-data-grid';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';

import {useStyles} from './Lectures.styles';
import useQuery from '../../../../hooks/useQuery';
import standardErrorHandler from '../../../../utils/standardErrorHandler';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import Typography from '@mui/material/Typography';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../../components/shared/SectionHeader/SectionHeader';
import ListHeader from '../../../../components/shared/ListHeader/ListHeader';
import Divider from '../../../../components/shared/Divider/Divider';
import LectureItem from '../../../../components/core/LectureItem/LectureItem';

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
    `/api/public/static${row.static_file.path}/${row.static_file.filename}`
  );
  return (
    <StandardLayout>
      <SectionHeader isPage title = 'Lectures'/>
      <Divider />
      <ListHeader sections = {['Course', 'Post Time', 'Title', 'Lecture Attachment']} />
      {lectures.map((lecture, index) => (
        <LectureItem
          key = {`${lecture.name}-${index}`}
          course = {lecture.course}
          postTime = {lecture.post_time}
          title = {lecture.title}
          id = {lecture.id}
          fileAttachment = {get_href(lecture)}
        />
      ))}
    </StandardLayout>
  );
};

export default Lectures;
