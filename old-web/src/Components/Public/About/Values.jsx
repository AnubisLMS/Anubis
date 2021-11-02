import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Grid from '@material-ui/core/Grid';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';

import IconButton from '@material-ui/core/IconButton';
import CodeIcon from '@material-ui/icons/Code';
import SupervisorAccountIcon from '@material-ui/icons/SupervisorAccount';
import GrainIcon from '@material-ui/icons/Grain';
import Divider from '@material-ui/core/Divider';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  container: {
    display: 'flex',
    position: 'relative',
    [theme.breakpoints.down('md')]: {
      marginTop: theme.spacing(5),
      marginBottom: theme.spacing(5),
    },
    [theme.breakpoints.up('md')]: {
      margin: theme.spacing(15),
    },
  },
  item: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: theme.spacing(0, 5),
  },
  icon: {
    fontSize: 64,
  },
  title: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(0),
  },
  description: {
    fontSize: '24px',
  },
  divider: {
    width: 120,
    height: 3,
    backgroundColor: 'white',
    margin: theme.spacing(3, 0),
  },
}));

const values = [
  {
    Icon: CodeIcon,
    title: 'Cloud IDEs',
    description:
      'Give students a consistent, reliable linux environment accessible from ' +
      'anywhere in the world at a touch of a button. No more are class VMs or ' +
      'asking students to install extra software.',
  },
  {
    Icon: SupervisorAccountIcon,
    title: 'Administration',
    description:
      'Get meaningful usage statistics and other insights about your assignments. ' +
      'Create and manage assignments without installing anything extra using the ' +
      'Anubis Management Cloud IDEs.',
  },
  {
    Icon: GrainIcon,
    title: 'Scale',
    description:
      'Since we don\'t use VMs, we can handle a whole lot of students on our ' +
      'servers. Our lightweight Cloud IDEs allow us to provide responsive development ' +
      'environment to hundreds of users at once.',
  },
];

export default function Values() {
  const classes = useStyles();

  return (
    <div className={classes.root} id={'values'}>
      <Paper>
        <Container className={classes.container}>
          <Grid container spacing={4}>
            {values.map(({Icon, title, description}) => (
              <Grid item xs={12} md={4} key={title}>
                <div className={classes.item}>
                  <IconButton>
                    <Icon color={'primary'} className={classes.icon}/>
                  </IconButton>
                  <Typography variant="h6" className={classes.title}>
                    {title}
                  </Typography>
                  <Divider variant={'middle'} className={classes.divider} />
                  <Typography color={'textSecondary'} className={classes.description}>
                    {description}
                  </Typography>
                </div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Paper>
    </div>
  );
}
