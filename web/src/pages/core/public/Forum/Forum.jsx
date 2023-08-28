import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import useTheme from '@mui/material/styles/useTheme';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import PostListItem from '../../../../components/forums/PostListItem/PostListItem';
import Post from '../../../../components/forums/Post/Post';
import CreateDialog from '../../../../components/forums/CreateDialog/CreateDialog';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';

import CreateIcon from '@mui/icons-material/Create';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import RefreshIcon from '@mui/icons-material/Refresh';

export default function Forum() {
  const {enqueueSnackbar} = useSnackbar();
  const theme = useTheme();

  const [courses, setCourses] = useState(undefined);
  const [selectedCourse, setSelectedCourse] = useState(null);

  const [posts, setPosts] = useState([{
    title: 'Sample Post',
    category: 'Sample Category',
    content: {
      'blocks': [{
        'key': '4f5r7', 'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
        'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
        'entityRanges': [], 'data': {},
      }], 'entityMap': {},
    },
    display_name: 'Sample User',
    created: 1689602823000,
    seen_count: 0,
    comments: [{
      display_name: 'Rami',
      content: {
        'blocks': [{
          'key': '4f5r7',
          'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
          'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
          'entityRanges': [], 'data': {},
        }], 'entityMap': {},
      },
      children: [{
        display_name: 'Rami', children: [], content: {
          'blocks':
            [{
              'key': '4f5r7',
              'text': 'dfgsdfgsddfsjfdfj', 'type': 'unstyled',
              'depth': 0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
              'entityRanges': [], 'data': {},
            }], 'entityMap': {},
        },
      }],
    }],
  }]);
  const [selectedPost, setSelectedPost] = useState(undefined);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    axios.get('/api/public/courses/')
      .then((response) => {
        const data = standardStatusHandler(response, enqueueSnackbar);
        if (data) {
          setCourses(data.courses);
          setSelectedCourse(data.courses[0]);
        }
      })
      .catch(standardErrorHandler(enqueueSnackbar));
    // setInterval(() => {
    //   refreshPosts(false);
    // }, 15000);
  }, []);

  useEffect(() => {
    if (!selectedCourse) {
      return undefined;
    }
    refreshPosts();
  }, [selectedCourse]);

  const refreshPosts = async (select_post = true) => {
    if (!selectedCourse) {
      standardErrorHandler(enqueueSnackbar)(new Error('No course selected'));
      return undefined;
    }
    axios.get(`/api/public/forum/course/${selectedCourse.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setPosts(data.posts);
        if (select_post) setSelectedPost(data.posts[0]);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const refreshSelectedPost = async () => {
    if (!selectedPost) {
      standardErrorHandler(enqueueSnackbar)(new Error('No post selected'));
      return undefined;
    }
    axios.get(`/api/public/forum/post/${selectedPost.id}`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setSelectedPost(data.post);
        // Find and update data in post array for consistency do this instead of wasting an api call
        setPosts(posts.map((post) => post.id === data.post.id ? data.post : post));
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  };

  const handleCourseSelect = React.useCallback((e) => {
    // console.log(e.target.value);
    setSelectedCourse(e.target.value);
  }, []);

  const handleCreatePost = React.useCallback((post) => {
    axios.post(`/api/public/forum/post`, {...post, course_id: selectedCourse.id})
      .then(() => {
        refreshPosts();
        setIsDialogOpen(false);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedCourse]);

  const handleEditPost = React.useCallback((post) => {
    axios.patch(`/api/public/forum/post/${selectedPost.id}`, {...post})
      .then(() => {
        refreshSelectedPost();
        setIsDialogOpen(false);
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedPost]);

  const handleCreateComment = React.useCallback((comment) => {
    const {parent_id = null} = comment;
    const endpoint = (
      parent_id ?
        `/api/public/forum/post/${selectedPost.id}/comment/${parent_id}` :
        `/api/public/forum/post/${selectedPost.id}/comment`
    );
    axios.post(endpoint, {
      content: comment?.content,
      anonymous: comment?.anonymous,
    })
      .then((r) => {
        standardStatusHandler(r, enqueueSnackbar);
        refreshSelectedPost();
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedPost]);

  const handleEditComment = React.useCallback((id, comment) => {
    axios.patch(`/api/public/forum/post/comment/${id}`, {
      content: comment?.content,
      anonymous: comment?.anonymous,
    })
      .then((r) => {
        standardStatusHandler(r, enqueueSnackbar);
        refreshSelectedPost();
      })
      .catch(standardErrorHandler(enqueueSnackbar));
  }, [selectedPost]);

  return (
    <StandardLayout>
      <CreateDialog
        open={isDialogOpen}
        setOpen={setIsDialogOpen}
        handleCreatePost={handleCreatePost}
      />
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        pt: 1, pb: 1,
        pr: 3, pl: 3,
        mt: 2,
        borderRadius: '5px',
        border: `1px solid ${theme.palette.dark.blue['200']}`,
      }}>
        <Box sx={{display: 'flex', alignItems: 'center', gap: 2}}>
          <Typography>
            Forum
          </Typography>
          {selectedCourse && (
            <Box sx={{}}>
              <Select
                sx={{
                  pb: 1, pt: 1,
                  pl: 2, pr: 2,
                  // border: `1px solid ${theme.palette.dark.blue['200']}`,
                  // borderRadius: .5,
                }}
                value={selectedCourse}
                onChange={handleCourseSelect}
              >
                {courses && courses.map((course, index) => (
                  <MenuItem
                    key={`${course.name}-${index}`}
                    value={course}
                  >
                    {course.course_code}
                  </MenuItem>
                ))}
              </Select>
            </Box>
          )}
          <Button
            variant={'contained'}
            color={'primary'}
            onClick={refreshPosts}
          >
            <RefreshIcon/>
          </Button>
        </Box>
        <Button
          variant={'contained'}
          color={'primary'}
          onClick={() => setIsDialogOpen(true)}
        >
          New Post
          <CreateIcon/>
        </Button>
      </Box>

      <Grid container sx={{
        mt: 2,
        width: '100%',
        minHeight: '900px',
      }}>
        <Grid item xs={3} sx={{
          borderLeft: `1px solid ${theme.palette.dark.blue['200']}`,
          borderTop: `1px solid ${theme.palette.dark.blue['200']}`,
          borderBottom: `1px solid ${theme.palette.dark.blue['200']}`,
          borderRadius: '5px 0px 0px 5px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 1,
          padding: 1,
        }}>
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
        <Grid item xs={9} sx={{
          border: `1px solid ${theme.palette.dark.blue['200']}`,
          borderRadius: '0px 5px 5px 0px',
        }}>
          {selectedPost && (
            <Post
              key={selectedPost.id}
              title={selectedPost.title}
              content={selectedPost.content}
              user={selectedPost.display_name}
              ownedByMe={selectedPost.owned_by_me}
              seenCount={selectedPost.seen_count}
              createdDate={selectedPost.created}
              updatedDate={selectedPost.last_updated}
              comments={selectedPost.comments}
              handleCreateComment={handleCreateComment}
              handleEditComment={handleEditComment}
              handleEditPost={handleEditPost}
            />
          )}
        </Grid>
      </Grid>
    </StandardLayout>
  );
}

