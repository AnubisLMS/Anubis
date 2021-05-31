import React from 'react';

import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';


const useStyles = makeStyles((theme) => ({
  usage: {
    height: 0,
    paddingTop: '83.33%', // 16:9
  },
  title: {
    padding: theme.spacing(1, 2),
    fontSize: 16,
  },
}));

export default function Visuals() {
  const classes = useStyles();

  return (
    <Grid container spacing={2} justify={'center'}>
      <Grid item xs={12}>
        <Typography variant="h6">
          Anubis
        </Typography>
        <Typography variant={'subtitle1'} color={'textSecondary'}>
          Visuals
        </Typography>
      </Grid>
      <Grid item/>
      <Grid item xs={12} sm={12} md={10} lg={8} xl={6}>
        <Card className={classes.card}>
          <CardHeader
            avatar={<Avatar src={'/logo512.png'}/>}
            title={'Anubis Usage Over Time'}
            titleTypographyProps={{variant: 'h6'}}
            subheader={'re-generated every 5 minutes'}
          />
          <CardMedia
            className={classes.usage}
            image={'/api/public/visuals/usage'}
            title={'Anubis Usage'}
          />
        </Card>
      </Grid>
    </Grid>
  );
}
