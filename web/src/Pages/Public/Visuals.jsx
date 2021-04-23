import React, {useState} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import {useSnackbar} from 'notistack';
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import Paper from '@material-ui/core/Paper';
import {
  XYPlot,
  XAxis,
  YAxis,
  HorizontalGridLines,
  VerticalGridLines,
  LineSeries,
} from 'react-vis';
import axios from 'axios';
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
}));

export default function Visuals() {
  const classes = useStyles();
  const {enqueueSnackbar} = useSnackbar();
  const [usageData, setData] = useState([]);

  React.useEffect(() => {
    axios.get('/api/public/visuals/raw-usage').then((response) => {
      const _data = standardStatusHandler(response, enqueueSnackbar);
      if (_data.usage) {
        setData(_data.usage);
      }
    }).catch(standardErrorHandler(enqueueSnackbar));
  }, []);

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
      <Grid item xs={12}>
        <div style={{display: 'flex', justifyContent: 'center'}}>
          <Paper style={{width: 620}}>
            <Typography variant={'subtitle1'} className={classes.title}>
            Submissions over time
            </Typography>
            <XYPlot xType="time" width={600} height={300}>
              <HorizontalGridLines />
              <VerticalGridLines />
              <XAxis title="time" />
              <YAxis title="count" />
              {(usageData ?? []).map(({name, data}) => (
                <LineSeries
                  key={name}
                  data={data.map(({x, y}) => ({x: new Date(x), y}))}
                />
              ))}
            </XYPlot>
          </Paper>
        </div>
      </Grid>
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
