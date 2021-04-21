import React from 'react';
import CardActionArea from '@material-ui/core/CardActionArea';
import {Link as RouterLink} from 'react-router-dom';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import Link from '@material-ui/core/Link';
import BlogImg from './BlogImg';


export default function TheiaIDEPost({classes, preview = false}) {
  return (
    <Card className={classes.card}>
      <CardActionArea {...(!!preview ? {component: RouterLink, to: preview} : {})}>
        <CardHeader
          avatar={<Avatar src={'https://avatars.githubusercontent.com/u/36013983'}/>}
          title={'Anubis cloud IDEs'}
          titleTypographyProps={{variant: 'h6'}}
          subheader={'2021-04-13'}
        />
        <CardContent>

          <Typography className={classes.typography}>
            One of the more exciting new features of Anubis is that of the cloud ide. Leveraging some magic
            that
            <Link href={'https://kubernetes.io/docs/concepts/workloads/pods/'} target={'_blank'}>
              {' '}Kubernetes pods{' '}
            </Link>
            give us, we can provide a fully isolated IDE environment for all
            ~130 students in Intro to OS concurrently.
          </Typography>

          {!preview ? (
            <React.Fragment>
              {/* Theia IDE */}
              <BlogImg
                src={'/api/public/static/80edb046dfae7c0f'}
                alt={'theia-logo.png'}
              />
              <Typography className={classes.subheader}>
                Theia IDE
              </Typography>
              <Typography className={classes.typography}>
                Each Anubis Cloud IDE is a
                <Link href={'https://theia-ide.org/'} target={'_blank'}>{' '}Theia IDE{' '}</Link>
                server. Theia is a essentially a VSCode webserver. With theia, we can install most any regular vscode
                extension. The Theia project also maintains docker images for specific language targets. Using
                these official docker images at a starting point, we can specialize builds of theia to support
                specific environments.
              </Typography>
              <Typography className={classes.typography}>
                Something very special about theia is that we can actually build theia using a package.json. By doing
                this we are able to compile in only the plugins we actually need/use. This is very useful because we can
                bring the default theia-cpp image down from 4GiB to ~1.5GiB. This is still an annoyingly large image,
                but hey, {'it\'s'} not 4GiB.
              </Typography>
              <Typography className={classes.typography}>
                In this new optimized build of theia, we cut out all the extra stuff that exists in the normal theia-cpp
                image, and add the extra packages that we need for xv6. For example, we can install qemu and libc6-i386
                so that we can build and run xv6.
              </Typography>
              <Typography className={classes.typography}>
                The optimization does not end there. Anubis supports using specific IDE builds for specific
                assignments. What this means is that we can have specific IDEs for specific assignments. For some
                classes, the dependencies that are necessary can be annoying to install on different individuals
                machines. With Anubis, you just need to make it work in the cloud IDE, then a stable and consistent
                environment is available to all students.
              </Typography>

              {/* Theia IDE Frontend */}
              <Typography className={classes.subheader}>
                IDE Frontend
              </Typography>
              <Typography className={classes.typography}>
                Once students have created their repo, they will be able to launch a theia session for a given
                assignment. At that time, we clone exactly what is in github into a theia pod.
              </Typography>
              <BlogImg
                src={'/api/public/static/f43c253a3c781101'}
                alt={'theia1'}
              />
              <Typography className={classes.typography}>
                Once their session pod has been allocated, then they can click the goto session button. It is at this
                point that their requests start to go through the theia proxy. Assuming all goes well with initializing
                the session, and starting the websocket connection, then students will have the following theia IDE.
              </Typography>
              <BlogImg
                src={'/api/public/static/002315b86f8b557f'}
                alt={'theia2'}
              />
              <Typography className={classes.typography}>
                Something to point out here is that this looks, feels, and acts exactly as VSCode, but it is accessed
                over the internet. We can even load some VSCode plugins into the builds.
              </Typography>


              {/* Theia Pod Design */}
              <Typography className={classes.subheader}>
                Theia Pod Design
              </Typography>
              <Typography className={classes.typography}>
                The pod design requires some distributed finesse. There are a couple of things about theia that make it
                so that we need to do some rather fancy things in Kubernetes to make the setup work.
              </Typography>
              <Typography className={classes.typography}>
                Distributing and handling multiple theia severs and concurrent connections is the name of the game here.
                We need to be able to have a setup that scales well that is able to handle many users on the system at
                once.
              </Typography>
              <Typography className={classes.typography}>
                The main thing that we need to handle is the fact that theia requires a websocket connection between the
                browser and theia server instance. When the pods are allocated, we note the ClusterIP in the database.
                Then when we need to initialize a client session, we use this saved ClusterIP to forward requests (both
                http and websockets) to the pod.
              </Typography>
              <BlogImg
                src={'/api/public/static/0de69b0786007e60'}
                alt={'theia-init-1'}
              />
              <Typography className={classes.typography}>
                These pods are temporary. When the student is finished working (or after a timeout) we reclaim the
                resources by deleting the containers and data. Because of this, we needed some form of autosave. Saving
                is pushing to github. The issue we need to contend with is how to have automatic commits and pushes
                to github without exposing a password or api token to the users.
              </Typography>
              <Typography className={classes.typography}>
                The solution to this dilemma is to have a second sidecar container whose only role is committing and
                pushing to github. The credentials live in that container, completely separate and inaccessible to the
                user who may be working in the other theia server container. These two containers are connected by a
                shared <Link href={'https://rancher.com/products/longhorn/'} target={'_blank'}>{' '}longhorn{' '}</Link>
                volume. This volume is relatively small (~50MiB). With this setup, we have autosave
                running in the background while staying completely hidden from the user.
              </Typography>
              <BlogImg
                src={'/api/public/static/9e023fa2714d8cdd'}
                alt={'theia-pod.mmd.png'}
              />

              <Typography className={classes.subheader}>
                Scalability of Cloud IDE
              </Typography>
              <Typography className={classes.typography}>
                With these lightweight containerized theia servers, we are able to support significantly more concurrent
                users than if we had elected to implement a cloud vm solution. Because these are containers and we do
                not need to virtualize hardware, the resources on the system for each user is significantly less. Given
                the resources that we have in the Space Cluster, we would be able to have maybe 20-30 concurrent users
                using cloud virtual machines. With our containerized theia, we can handle all ~130 students at the same
                time with room to breath.
              </Typography>

              {/* Reclaiming Theia Resources */}
              <Typography className={classes.subheader}>
                Reclaiming Theia Resources
              </Typography>
              <Typography className={classes.typography}>
                The theia sessions are often forgotten about. Students will create an IDE server, work on it for a bit,
                then forget manually close it. Due to this, we have a time to live of 6 hours for each session. A
                cronjob runs every 5 minutes to look for and schedule delete for stale resources. We do provide a button
                in the anubis panel as a way for students to manually schedule their session for deletion. Even when we
                ask students to click this button when they are done, some still do not. In the following graph we can
                see an interesting experiment in student behavior. It shows a cumulative graph showing the duration of a
                theia session for the final exam. Just about 40% of sessions hit the 6-hour timeout.
              </Typography>
              <BlogImg
                src={'/api/public/static/52f59217b8caaa02'}
                alt={'theia3'}
              />


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
