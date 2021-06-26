import React from 'react';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';

import StandardLayout from '../../Components/Layouts/StandardLayout';
import Button from '@material-ui/core/Button';
import CloudDownload from '@material-ui/icons/CloudDownload';


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
}));


export default function Visuals() {
  const classes = useStyles();

  return (
    <StandardLayout description={'Visuals'}>
      <Grid container spacing={4} justify={'center'}>
        <Grid item xs>
          <Card>
            <CardHeader
              avatar={<Avatar src={'/logo512.png'}/>}
              title={'Anubis Usage Over Time'}
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
              href={'/api/public/visuals/usage'}
              download={'anubis-usage.png'}
            >
              Download
            </Button>
            <CardMedia
              className={classes.usage}
              image={'/api/public/visuals/usage'}
              title={'Anubis Usage'}
            />
          </Card>
        </Grid>
      </Grid>
    </StandardLayout>
  );
}
