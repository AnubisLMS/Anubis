import React from 'react';
import {useHistory} from 'react-router-dom';

import SchoolIcon from '@material-ui/icons/School';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Item from '../../shared/Item/Item';
import {useStyles} from './CourseItem.styles';

const CourseItem = ({
  name,
  section,
  instructor,
  assignments,
  id,
}) => {
  const history = useHistory();
  const classes = useStyles();

  return (
    <Item
      showStatus={false}
      title={name}
      subTitle={`Course Section ${section}`}
      titleIcon={<SchoolIcon/>}
      link={`/course?courseId=${id}`}
    >
      <Typography className={classes.instructorText}>{instructor}</Typography>
      <Typography className={classes.assignmentsText}>{assignments} Assignments</Typography>
      <Button onClick={() => history.push(`/courses/assignments?courseId=${id}`)}>
        View Course
      </Button>
    </Item>
  );
};

export default CourseItem;
