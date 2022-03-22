import React from 'react';
import {useHistory} from 'react-router-dom';

// Reference for Icons: https://mui.com/components/material-icons/?query=assignment
import FeaturedVideoIcon from '@material-ui/icons/FeaturedVideo';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Item from '../../shared/Item/Item';
import {useStyles} from './LectureItem.styles';

const LectureItem = ({
  course,
  postTime,
  title,
  id,
  fileAttachment,
}) => {
  const history = useHistory();
  const classes = useStyles();

  return (
    <Item
      showStatus = {false}
      title = {course}
      subTitle = {`from: ${course}`}
      titleIcon = {<FeaturedVideoIcon/>}
      link = {fileAttachment}
    >
      <Typography className = {classes.postTimeText}>{postTime}</Typography>
      <Typography>{title}</Typography>
      <Button onClick = {() => history.push(fileAttachment)}>
        View Lecture Attachment
      </Button>
    </Item>
  );
};

export default LectureItem;
