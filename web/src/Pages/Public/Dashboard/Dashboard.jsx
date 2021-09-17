import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {useSnackbar} from 'notistack';

import {Link} from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Grow from '@material-ui/core/Grow';

import CourseCard from '../../../Components/Public/Courses/CourseCard/CourseCard';
import StandardLayout from '../../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../../Utils/standardStatusHandler';
import standardErrorHandler from '../../../Utils/standardErrorHandler';
import {useStyles} from './Dashboard.styles';

const Dashboard = () => {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    axios.get('/api/public/courses/').then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data) {
        setCourses(data.courses);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  const SectionContainer = ({children, title, link, linkTitle}) => (
    <Box className={classes.sectionContainer}>
      <Box className={classes.sectionHeader}>
        <Typography className={classes.sectionHeaderTitle}>
          {title}
        </Typography>
        <Link to={link} className={classes.sectionHeaderLink}>
          {linkTitle}
        </Link>
      </Box>
      <Box className={classes.sectionChildContainer}>
        {children}
      </Box>
    </Box>
  );

  return (
    <StandardLayout>
      <SectionContainer title={'Courses'} link={'/courses'} linkTitle={'View All Courses'}>
        <Grid container spacing={4}>
          {courses.map((course, pos) => (
            <Grid item key={course.courseCode}>
              <Grow
                in={true}
                style={{transformOrigin: '0 0 0'}}
                timeout={300 * (pos + 1)}
              >
                <CourseCard {... course}/>
              </Grow>
            </Grid>
          ))}
        </Grid>
      </SectionContainer>
      <SectionContainer title={'Active Assignments'}>
      </SectionContainer>
      <SectionContainer title={'Past Assignments'}>
      </SectionContainer>
    </StandardLayout>
  );
};

export default Dashboard;
