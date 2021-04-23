import React from 'react';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import {Link as RouterLink} from 'react-router-dom';
import Link from '@material-ui/core/Link';
import BlogImg from './BlogImg';
import {Image} from '@material-ui/icons';

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

              {/* RPC in Anubis */}
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
                a job is put in the RPC queue. There is then a pool of workers in the
                form of a{' '}
                <Link
                  href={'https://kubernetes.io/docs/concepts/workloads/controllers/deployment/'}
                  target={'_blank'}
                >
                  Kubernetes deployment
                </Link>
                . Each of these workers is constantly trying to dequeue and run
                the current job.
              </Typography>
              <BlogImg
                src={'/api/public/static/1c8d3c4d408e2187'}
                alt={'deployment'}
              />
              {/* END RPC in Anubis */}


              {/* Bulk Regrades */}
              <Typography className={classes.subtitle}>
                Bulk Regrades
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                A bulk regrade is where we regrade a large number of assignment submissions.
                Any time the test cases change while an assignment is out, I will run a full
                bulk regrade. These operations are probably when Anubis is under the highest
                sustained load. Some assignments can get up to 5,000+ individual submissions
                that would need to be regraded. On their own and over time, this is quite
                minimal load. Even on the night of a deadline, there are rarely more than 3
                concurrent submission jobs.
              </Typography>
              <Typography gutterBottom className={classes.sidebar}>
                It takes so long to enqueue all the rpc calls, that the function to bulk regrade
                an assignment is itself an RPC call. It enqueues batch jobs that enqueue 100
                individual submission jobs to the RPC queue. This was the fastest way to get
                around things timing out!
              </Typography>
              <Typography gutterBottom className={classes.typography}>
               This is one of the places I have introduced artificial limits into Anubis. If
               we were to say create a kubernetes job for each submission all at once, we will
               reach limits within the kubernetes API quite quickly. It is much better to have
               some set artificial limit of kubernetes submission jobs that can be running at
               any time. We do this right in the RPC job. If there are too many jobs that are
               running, then we re-enqueue the rpc job.
              </Typography>
              <BlogImg
                src={'/api/public/static/110314255258e8a0'}
                alt={'rpc-max-jobs'}
              />
              {/* END Bulk Regrades */}


              {/* Midterm Perfect Storm */}
              <Typography className={classes.subtitle}>
                Midterm Perfect Storm
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                This setup worked just fine for quite a while. What got in the way was
                scale. The majority of the time, the RPC queue is basically empty. It
                is only when users are on, or there is a bulk regrade that there are items
                in the queue.
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                Now consider the situation where there is a bulk regrade while there are
                users online. This is the exact situation I found myself in while
                the midterm was running. There were several changes to the assignment tests
                that happened while the test was running. The midterm also only ran for
                48 hours. This caused the perfect storm. There were consistently 50+
                users online while I needed to run bulk regrade jobs.
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                The result of this situation was that the RPC queues were saturated with thousands
                of individual submissions. This made it so that if you went to start a Cloud IDE,
                the spinner would just keep spinning. <i>Let me demonstrate...</i>
              </Typography>
              <BlogImg
                src={'/api/public/static/88a52255687d6d56'}
                alt={'rpc-queue-1'}
              />
              <Typography gutterBottom className={classes.typography}>
                Imagine this is our RPC queue while a bulk regrade is running. The {'"..."'} is meant to
                represent the hundreds if not several thousands of submission jobs in the queue at that time.
                Now if someone clicks the button to start a new Cloud IDE at that time, then it would be thrown
                into the same job queue.
              </Typography>
              <BlogImg
                src={'/api/public/static/6474ac1290150bfc'}
                alt={'rpc-queue-2'}
              />
              <Typography gutterBottom className={classes.typography}>
                The problem is that the queue is much too saturated with the submission jobs. The start
                theia job should have higher priority than a regrade job, but this model does not support
                that. The job will sit in the queue for much too long while the student will become
                frustrated. All they can see in this situation is the infinite spinner. For many
                students, the Anubis Cloud IDE is what they rely on to do their OS work. If it does not
                work, then they do not have or know how to set up an alternative environment.
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                This problem was something I had known about for a while. Despite this, this {'"perfect storm" '}
                situation was so infrequent that it was something I deemed not worthy of the time to fix.
                Whoops, that was that a mistake.
              </Typography>
              {/* END Midterm Perfect Storm */}


              {/* The Solution */}
              <Typography className={classes.subtitle}>
                The Solution
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                The fix I choose to this problem was splitting the RPC system into two queue&apos;s and
                two worker pools. What made this a highly stressful patch is that there were 50+
                students on Cloud IDEs at this time. If the deploy was unsuccessful, or there was a new
                bug introduced, then many students midterm work would be interrupted. Regardless, the
                problems this design flaw introduced outweighed the risks.
              </Typography>
              <BlogImg
                src={'/api/public/static/079fde3fe6191089'}
                alt={'rpc-queue-3'}
              />
              <Typography gutterBottom className={classes.typography}>
                The first step was changing all the places that rpc functions are called so that they
                specified a queue to place the job in. I choose there to be a &apos;default&apos;,
                and &apos;theia&apos; queues. In the interest of consolidation, I had from the start put
                all the RPC functions into a single file. All that needed to be done here was specify
                either default or theia queue for each of these functions.
              </Typography>
              <BlogImg
                src={'/api/public/static/3e79ceea4984cdbe'}
                alt={'rpc-functions'}
              />
              <Typography gutterBottom className={classes.typography}>
                The next step is adding a second worker pool for the theia queue. This is pretty much
                just copy and paste the kubernetes yaml definition for the rpc-default deployment
                and find-replace &apos;default&apos; with &apos;theia&apos;.
              </Typography>
              <BlogImg
                src={'/api/public/static/ee5af57fa37971ce'}
                alt={'rpc-both'}
              />
              <Typography gutterBottom className={classes.typography}>
                The last step is by far the most important. <b>Testing everything.</b> I loaded
                Anubis up into a minikube cluster locally and made sure everything was working right.
                Cloud IDEs were getting created right. So were bulk regrades and submission processing
                jobs.
              </Typography>
              {/* END The Solution */}


              {/* Deploying the Patch */}
              <Typography gutterBottom className={classes.subtitle}>
                Deploying the Patch
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                Once I was as confident as I could be, I did the deploy. It was a helm upgrade, then
                a rolling restart of all the components that changed. The worker pools, and the api.
                It seems that no matter how long I do these types of deploys, they never get comfortable.
                It is almost like the more deploys I do, the more stressful they become.
              </Typography>
              <BlogImg
                src={'/api/public/static/b67a5c186ab65ce2'}
                alt={'deploy-anxiety'}
              />
              <Typography gutterBottom className={classes.typography}>
                The deploy itself only took about a minute. The thing that took the longest was
                the nodes pulling the updated images from the registry. Thankfully, everything just worked.
                The old RPC worker pool was replaced with the two new ones. The RPC function calls were properly
                putting jobs in the right place. This new arrangement alleviated the issues immediately.
                Students could start their IDEs with no delay, and I could do my bulk regrades.
              </Typography>
              {/* END Deploying the Patch */}

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
