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
import CreateIcon from '@mui/icons-material/Create';

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
  const [selectedCourse, setSelectedCourse] = useState(2);
  const [selectedCourseCode, setSelectedCourseCode] = useState('');

  const [posts, setPosts] = useState([{
    title: 'Sample Post',
    category: 'Sample Category',
    content: {'blocks': [{'key': '4f5r7', 'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
      'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
      'entityRanges': [], 'data': {}}], 'entityMap': {}},
    display_name: 'Sample User',
    created: 1689602823000,
    seen_count: 0,
    comments: [{display_name: 'Rami', children: [{display_name: 'Rami', children: [], content: {'blocks':
    [{'key': '4f5r7',
      'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
      'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
      'entityRanges': [], 'data': {}}], 'entityMap': {}}}], content: {'blocks': [{'key': '4f5r7',
      'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
      'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
      'entityRanges': [], 'data': {}}], 'entityMap': {}}}],
  }]);
  const [selectedPost, setSelectedPost] = useState(undefined);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
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

  // useEffect(() => {
  //   if (!selectedPost) {
  //     return undefined;
  //   }

  //   axios.get(`api/public/forums/post/${selectedPost.id}`)
  //     .then((response) => {
  //       const data = standardStatusHandler(response, enqueueSnackbar);
  //       console.log(data.post);
  //       if (data) {
  //         setSelectedContent(data.post);
  //       }
  //     })
  //     .catch(standardErrorHandler(enqueueSnackbar));
  // }, [selectedPost]);

  const handleCourseSelect = (e) => {
    console.log(e.target.value);
    setSelectedCourse(e.target.value);
  };

  const handleCreatePost = (post) => {
    // console.log(post);
    axios.post(`/api/public/forums/post`, {...post, course_id: selectedCourse.id})
      .then(() => {
        setRefreshPosts(refreshPosts + 1);
        setIsDialogOpen(false);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleCreateComment = (comment) => {
    axios.post(`/api/public/forums/comment`, {...comment, post_id: selectedPost.id, course_id: selectedCourse.id})
      .then(() => {
        // Need to refresh comments
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  };
  return (
    <StandardLayout>
      <CreateDialog
        open={isDialogOpen}
        setOpen={setIsDialogOpen}
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
          onClick={() => setIsDialogOpen(true)}
        >
          New Post
          <CreateIcon className={classes.newPostIcon} />
        </Button>
      </Box>
      <Grid container className={classes.postsContainer}>
        <Grid item xs={3} className={classes.postListContainer}>
          {posts?.length > 0 && posts.map((post, index) => (
            <PostListItem
              key={`${post.title}-${index}`}
              title={post.title}
              category={post.category}
              content={post.content?.blocks[0].text}
              user={post.display_name}
              date={post.created}
              seenCount={post.seen_count}
              isSelected={Boolean(selectedPost === post)}
              handleSelect={() => setSelectedPost(post)}
            />
          ))}
        </Grid>
        <Grid item xs={9} className={classes.postContentContainer}>
          {selectedPost && (
            <Post
              title={selectedPost.title}
              content={selectedPost.content}
              user={selectedPost.display_name}
              seenCount={selectedPost.seen_count}
              createdDate={selectedPost.created}
              updatedDate={selectedPost.last_updated}
              comments={selectedPost.comments}
              handleCreateComment={handleCreateComment}
            />
          )}
        </Grid>
      </Grid>
    </StandardLayout>
  );
}

