import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardHeader from '@mui/material/CardHeader';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CloudDownload from '@mui/icons-material/CloudDownload';
import Autocomplete from '@mui/lab/Autocomplete';
import TextField from '@mui/material/TextField';

import {useStyles} from './Visuals.styles';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';


const visuals = [
  {
    title: 'Anubis LMS Active Users Per Day In Last 2 Weeks',
    url: `/api/public/visuals/active/14/1`,
    filename: 'anubis-active-users-14-1.png',
  },
  {
    title: 'Anubis LMS Registered Users Last Year',
    url: `/api/public/visuals/users/365/1`,
    filename: 'anubis-registered-users-365-1.png',
  },
  {
    title: 'Anubis LMS Active Users Per Week In Last 3 Month',
    url: `/api/public/visuals/active/90/7`,
    filename: 'anubis-active-users-90-7.png',
  },
  {
    title: 'Anubis LMS Active Users Per Day In Last Half Year',
    url: `/api/public/visuals/active/180/1`,
    filename: 'anubis-active-users-180-1.png',
  },
  {
    title: 'Anubis LMS Active Users Per Month In Last Year',
    url: `/api/public/visuals/active/365/30`,
    filename: 'anubis-registered-users-365-30.png',
  },
  {
    title: 'Anubis Playgrounds Usage Over Time',
    url: `/api/public/visuals/playgrounds`,
    filename: 'anubis-playground-usage.png',
  },
];


const Visuals = () => {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [courses, setCourses] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    axios.get(`/api/public/courses/visuals-list`).then((response) => {
      const data = standardStatusHandler(response, enqueueSnackbar);
      if (data?.courses) {
        setCourses(data.courses);
        if (data.courses.length > 0) {
          setSelected(data.courses[0]);
        }
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

  return (
    <StandardLayout description={'Visuals'}>
      <Grid container spacing={4} justifyContent={'center'}>
        {visuals.map(({title, filename, url}, index) => (
          <Grid item xs sm={10} lg={8} xl={6} key={index}>
            <Card>
              <CardHeader
                avatar={<Avatar src={'/logo512.png'}/>}
                title={title}
                titleTypographyProps={{variant: 'h6'}}
                subheader={'re-generated every 5 minutes'}
              />
              <Button
                className={classes.button}
                startIcon={<CloudDownload/>}
                variant={'contained'}
                color={'primary'}
                size={'large'}
                component={'a'}
                href={url}
                download={filename}
              >
                Download
              </Button>
              <CardMedia
                className={classes.usage}
                image={url}
                title={title}
              />
            </Card>
          </Grid>
        ))}
        {selected && (
          <Grid item xs sm={10} lg={8} xl={6}>
            <Card>
              <CardHeader
                avatar={<Avatar src={'/logo512.png'}/>}
                title={'Anubis Course Usage Over Time'}
                titleTypographyProps={{variant: 'h6'}}
                subheader={'re-generated every 5 minutes'}
              />
              <div className={classes.autocomplete}>
                <Autocomplete
                  blurOnSelect
                  fullWidth={false}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label={'Select Course'}
                    />
                  )}
                  options={courses}
                  onChange={(_, course) => setSelected(course)}
                  getOptionLabel={(course) => `${course.course_code} - ${course.name}`}
                  value={selected}
                />
              </div>
              <Button
                className={classes.button}
                startIcon={<CloudDownload/>}
                variant={'contained'}
                color={'primary'}
                size={'large'}
                component={'a'}
                href={`/api/public/visuals/course/${selected?.id}`}
                download={`anubis-${selected?.id}-usage.png`}
              >
                Download
              </Button>
              <CardMedia
                className={classes.usage}
                image={`/api/public/visuals/course/${selected?.id}`}
                title={'Anubis Usage'}
              />
            </Card>
          </Grid>
        )}
      </Grid>
    </StandardLayout>
  );
};

export default Visuals;
