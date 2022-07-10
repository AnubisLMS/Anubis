import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import StandardLayout from '../../../components/shared/Layouts/StandardLayout';
import SectionHeader from '../../../components/shared/SectionHeader/SectionHeader';
import standardStatusHandler from '../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../utils/standardErrorHandler';
import PostListItem from '../../../components/forums/PostListItem/PostListItem';
import Post from '../../../components/forums/Post/Post';
import CreateDialog from '../../../components/forums/CreateDialog/CreateDialog';

import {useStyles} from './Forum.styles.jsx';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import RefreshIcon from '@mui/icons-material/Refresh';

export default function Forum({user}) {
  const {enqueueSnackbar} = useSnackbar();
  const classes = useStyles();

  const [courses, setCourses] = useState(undefined);
  const [selectedCourse, setSelectedCourse] = useState(undefined);
  const [selectedCourseCode, setSelectedCourseCode] = useState('');

  const [posts, setPosts] = useState(undefined);
  const [selectedPost, setSelectedPost] = useState(undefined);
  const [selectedContent, setSelectedContent] = useState(undefined);

  const [isDialogOpen, setIsDialogOpen] = useState(undefined);
  const [dialogMode, setDialogMode] = useState('post');

  const [refreshPosts, setRefreshPosts] = useState(0);

  const refresh = () => {
    setRefreshPosts(refreshPosts + 1);
  };

  useEffect(() => {
    axios.get('api/public/courses/')
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
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
      return undefined;
    }

    axios.get(`api/public/forums/course/${selectedCourse.id}`)
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        if (data) {
          setPosts(data.posts);
          setSelectedPost(data.posts[0]);
        }
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedCourse, refreshPosts]);

  useEffect(() => {
    if (!selectedPost) {
      return undefined;
    }

    axios.get(`api/public/forums/post/${selectedPost.id}`)
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        console.log(data.post);
        if (data) {
          setSelectedContent(data.post);
        }
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedPost]);

  const handleOpenDialog = (mode = 'post') => {
    setDialogMode(mode);
    setIsDialogOpen(true);
  };

  const handleCourseSelect = (e) => {
    console.log(e.target.value);
    setSelectedCourse(e.target.value);
  };

  const handleCreatePost = (post) => {
    axios.post(`/api/public/forums/post`, {...post, course_id: selectedCourse.id})
      .then(() => {
        setRefreshPosts(refreshPosts + 1);
        setIsDialogOpen(false);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  };

  return (
    <StandardLayout>
      <CreateDialog
        isOpen={isDialogOpen}
        mode={dialogMode}
        handleCreatePost={handleCreatePost}
      />
      <Box className={classes.controlsContainer}>
        <Box className={classes.controlsLeft}>
          <Typography>
            Forum
          </Typography>
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
            onClick={refresh}
          >
            <RefreshIcon />
          </Button>
        </Box>
        <Button
          className={classes.newPostButton}
          onClick={() => handleOpenDialog('post')}
        >
          Create New Post
        </Button>
      </Box>
      <Grid container className={classes.postsContainer}>
        <Grid item xs={3} className={classes.postListContainer}>
          {posts?.length > 0 && posts.map((post, index) => (
            <PostListItem
              key={`${post.title}-${index}`}
              title={post.title}
              category={post.category}
              user={post.display_name}
              date={post.created}
              seenCount={post.seen_count}
              isSelected={Boolean(selectedPost === post)}
              handleSelect={() => setSelectedPost(post)}
            />
          ))}
        </Grid>
        <Grid item xs={9} className={classes.postContentContainer}>
          {selectedContent && (
            <Post
              title={selectedContent.title}
              content={selectedContent.content}
              user={selectedContent.display_name}
              seenCount={selectedContent.seen_count}
              createdDate={selectedContent.created}
              updatedDate={selectedContent.last_updated}
              comments={selectedContent.comments}
            />
          )}
        </Grid>
      </Grid>
    </StandardLayout>
  );
}

