import React, {useEffect, useState} from 'react';
import {useSnackbar} from 'notistack';
import axios from 'axios';

import Autocomplete from '@material-ui/lab/Autocomplete';
import TextField from '@material-ui/core/TextField';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';

import CloudDownload from '@material-ui/icons/CloudDownload';

import StandardLayout from '../../Components/Layouts/StandardLayout';
import standardStatusHandler from '../../Utils/standardStatusHandler';
import standardErrorHandler from '../../Utils/standardErrorHandler';


const useStyles = makeStyles((theme) => ({
  usage: {
    height: 0,
    paddingTop: '83.33%', // 16:9
  },
  title: {
    padding: theme.spacing(1, 2),
    fontSize: 16,
  },
  button: {
    margin: theme.spacing(2, 1),
  },
  autocomplete: {
    paddingBottom: theme.spacing(1),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
  },
  paper: {
    flex: 1,
    padding: theme.spacing(1),
  },
}));


export default function Visuals() {
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
        <Grid item xs sm={10} lg={8} xl={8}>
          <Card>
            <CardHeader
              avatar={<Avatar src={'/logo512.png'}/>}
              title={'Anubis Usage Over Time'}
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
              download={'anubis-usage.png'}
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
      </Grid>
    </StandardLayout>
  );
}
