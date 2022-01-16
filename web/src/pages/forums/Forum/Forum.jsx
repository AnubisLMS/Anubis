import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../components/shared/SectionHeader/SectionHeader';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import PostListItem from '../../../components/forums/PostListItem/PostListItem';
import {useStyles} from './Forum.styles.jsx';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';


const fakePosts = [
  {
    title: 'Hello this is a test post',
    display_name: 'nysteo',
    category: 'general',
    created: new Date(),
  },
  {
    title: 'Anubis is dope',
    display_name: 'nysteo',
    category: 'general',
    created: new Date(),
  },
];

export default function Forum({user}) {
  const {enqueueSnackbar} = useSnackbar();
  const classes = useStyles();

  const [courses, setCourses] = useState(undefined);
  const [selectedCourse, setSelectedCourse] = useState(undefined);
  const [selectedCourseCode, setSelectedCourseCode] = useState('');

  const [posts, setPosts] = useState(undefined);

  const [refreshPosts, setRefreshPosts] = useState(0);

  const refresh = () => {
    setRefreshPosts(refreshPosts + 1);
  };

  useEffect(() => {
    axios.get('api/public/courses/')
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        console.log(data);
        if (data) {
          setCourses(data.courses);
          setSelectedCourse(data.courses[0]);
          setSelectedCourseCode(data.courses[0].course_code);
        }
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  useEffect(() => {
    if (!selectedCourse) {
      return null;
    }

    axios.get(`api/public/forums/course/${selectedCourse.id}`)
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        console.log(data);
        if (data) {
          setPosts(data);
        }
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedCourse]);

  const handleCourseSelect = (e) => {
    console.log(e.target.value);
    setSelectedCourse(e.target.value);
  };

  return (
    <StandardLayout>
      <Box className={classes.controlsContainer}>
        {selectedCourse && (
          <Box className={classes.courseSelectionContainer}>
            <Select
              classes={{
                root: classes.select,
              }}
              value={selectedCourseCode}
              onChange={handleCourseSelect}
              disableUnderline
            >
              {courses && courses.map((course, index) => (
                <MenuItem
                  key={`${course.name}-${index}`}
                  value={course.course_code}
                >
                  {course.course_code}
                </MenuItem>
              ))}
            </Select>
          </Box>
        )}
        <Button
          className={classes.newPostButton}
        >
          Create New Post
        </Button>
      </Box>
      <Grid container className={classes.postsContainer}>
        <Grid item xs={3} className={classes.postListContainer}>
          {fakePosts.map((post, index) => (
            <PostListItem
              key={`${post.title}-${index}`}
              title={post.title}
              category={post.category}
              user={post.display_name}
              date={post.created}
            />
          ))}
        </Grid>
        <Grid item xs={9} className={classes.postContentContainer}>

        </Grid>
      </Grid>
    </StandardLayout>
  );
}

