import React from 'react';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import {Link as RouterLink} from 'react-router-dom';
import Link from '@material-ui/core/Link';

export default function MidtermRetroPost({classes, preview = false}) {
  return (
    <Card className={classes.card}>
      <CardActionArea {...(!!preview ? {component: RouterLink, to: preview} : {})}>
        <CardHeader
          avatar={<Avatar src={'https://avatars.githubusercontent.com/u/36013983'}/>}
          title={'Reorganizing RPC While Under Load - The Midterm Retro'}
          titleTypographyProps={{variant: 'h6'}}
          subheader={'2021-04-06'}
        />
        <CardContent>

          <Typography className={classes.typography}>
            During the midterm this semester there were a few issues that came up. In this post,
            I&apos;m going to be explaining how I went about live patching the RPC queues while
            the cluster was running and under load from users.
          </Typography>

          {!preview ? (
            <React.Fragment>

              <Typography gutterBottom color={'textSecondary'} className={classes.subtitle}>
                RPC in Anubis
              </Typography>

              <Typography gutterBottom className={classes.typography}>
                <Link href={'https://en.wikipedia.org/wiki/Remote_procedure_call'} target={'_blank'}>
                  RPC, or remote procedural call
                </Link>
                {' '}is the core of many modern distributed systems. Anubis is no different.
                We heavily rely on RPC to handle starting new Cloud IDE servers,
                handling bulk regrades, and creating submission pipelines.
              </Typography>

              <Typography gutterBottom className={classes.typography}>
                Every time you click regrade, push a commit, or start a Cloud IDE,
                a job is put in the RPC queue. There is then a pool of workers
                in a{' '}
                <Link
                  href={'https://kubernetes.io/docs/concepts/workloads/controllers/deployment/'}
                  target={'_blank'}
                >
                  Kubernetes deployment
                </Link>
                .
              </Typography>

              <Typography variant={'body2'} className={classes.author}>
                - John Cunniff
              </Typography>
            </React.Fragment>
          ) : null}


        </CardContent>
      </CardActionArea>
    </Card>
  );
}
