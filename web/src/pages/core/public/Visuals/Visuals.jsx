import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import CloudDownload from '@material-ui/icons/CloudDownload';
import Autocomplete from '@material-ui/lab/Autocomplete';
import TextField from '@material-ui/core/TextField';

import {useStyles} from './Visuals.styles';
import StandardLayout from '../../../../components/shared/Layouts/StandardLayout';
import standardStatusHandler from '../../../../utils/standardStatusHandler';
import standardErrorHandler from '../../../../utils/standardErrorHandler';


const visuals = [
  {
    title: 'Anubis LMS Registered Users Last Year',
    url: `/api/public/visuals/users/last-year`,
    filename: 'anubis-registered-users-last-year.png',
  },
  {
    title: 'Anubis LMS Active Users Per Day In Last 2 Weeks',
    url: `/api/public/visuals/usage/active`,
    filename: 'anubis-active-users-2-weeks.png',
  },
  {
    title: 'Anubis LMS Active Users Per Week In Last 3 Month',
    url: `/api/public/visuals/usage/active-month`,
    filename: 'anubis-active-users-3-months.png',
  },
  {
    title: 'Anubis LMS Active Users Per Day In Last Half Year',
    url: `/api/public/visuals/usage/active-half-year`,
    filename: 'anubis-active-users-half-year.png',
  },
  {
    title: 'Anubis Playgrounds Usage Over Time',
    url: `/api/public/visuals/usage/playgrounds`,
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
      <Grid container spacing={4} justify={'center'}>
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
                href={`/api/public/visuals/usage/${selected?.id}`}
                download={`anubis-${selected?.id}-usage.png`}
              >
                Download
              </Button>
              <CardMedia
                className={classes.usage}
                image={`/api/public/visuals/usage/${selected?.id}`}
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
