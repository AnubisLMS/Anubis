import React from 'react';
import {useHistory} from 'react-router-dom';

// Reference for Icons: https://mui.com/components/material-icons/?query=assignment
import FeaturedVideoIcon from '@mui/icons-material/FeaturedVideo';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
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
    >
      <Typography className = {classes.postTimeText}>{postTime}</Typography>
      <Typography>{title}</Typography>
      <Button component="a" href={fileAttachment} target="_blank" rel="noreferer" onClick = {() =>
        history.push(fileAttachment)}>
          View Lecture Attachment
      </Button>
    </Item>
  );
};

export default LectureItem;
