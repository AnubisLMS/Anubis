import React from 'react';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardHeader from '@material-ui/core/CardHeader';
import Avatar from '@material-ui/core/Avatar';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import Link from '@material-ui/core/Link';
import BlogImg from './BlogImg';
import {Link as RouterLink} from 'react-router-dom';

export default function Assignments({classes, preview = false}) {
  return (
    <Card className={classes.card}>
      <CardActionArea {...(!!preview ? {component: RouterLink, to: preview} : {})}>
        <CardHeader
          avatar={<Avatar src={'https://avatars.githubusercontent.com/u/36013983'}/>}
          title={'How Assignments Work in Anubis'}
          titleTypographyProps={{variant: 'h6'}}
          subheader={'2021-03-24'}
        />
        <CardContent>

          <Typography className={classes.typography}>
            Assignment in Anubis work unlike any other homework solution. In most college classes,
            when students finish their work, they turn in a final copy into the professor. With Anubis,
            we eliminate this process by making it so that students turn in their homework simply by
            working on it.
          </Typography>

          {!preview ? (
            <React.Fragment>

              <Typography gutterBottom color={'textSecondary'} className={classes.subtitle}>
                Assignment Structure
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                Each student will get their very own private repository on github that is created from an
                assignment template. With this repository, students can work on their homework and submit by
                pushing to their repo. The Anubis servers track the repos and launch &quot;submission pipelines&quot;
                for each push. <i>More on that later...</i>
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                This process is designed to be seamless. The only thing students need to do is enter their github
                username into Anubis at the beginning of the semester. The student&apos;s github username, not their
                netid
                is tied to the repo. For this, we need to be able to match the student&apos;s github username to their
                NYU netid.
              </Typography>


              <Typography gutterBottom color={'textSecondary'} className={classes.subtitle}>
                Submission Pipelines
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                You may be now asking yourself what exactly submission pipelines are. They are the processes that
                actually do the autograding tests. These pipelines have evolved and changed greatly since Anubis
                version 1.0 and are complex multi stage jobs.
              </Typography>
              <BlogImg
                src={'https://anubis.osiris.services/api/public/static/b88665d8c43989e0'}
                alt={'submission flow svg'}
              />
              <Typography gutterBottom className={classes.typography}>
                Github first reports a push to the Anubis api by a webhook. At this point, the submission
                is registered. This is
                the first time Anubis can account for this work, so it is this time that is counted as the time of
                submission.
              </Typography>
              <Typography gutterBottom className={classes.sidebar}>
                I point out the submission times because we could have just trusted the git repo commit times and used
                those for the time of submission. But as you could probably guess commit timestamps are trivially easy
                to fake.
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                With the submission accounted for, a submission pipeline job is enqueued in the RPC queue. The
                reason for the queue is that there may be times when we actually have more submissions that need
                to be run than can be run at a single time. By forcing jobs to go into a queue, we can set artificial
                limits on how many submission pipelines can be run at a single time. While students are working
                these limits are almost never reached, but imagine we need to regrade all the submissions for
                an assignment at once. Some assignments can get up to 3000 submissions. We then really need to
                queue up the pipelines so only some number are run at a single time.
              </Typography>
              <Typography gutterBottom className={classes.sidebar}>
                RPC or remote procedural call is where you essentially ask some remote application to do some
                specified work. RPC is core to a great deal of distributed systems, Anubis included. We will see
                more RPC later...
              </Typography>
              <Typography gutterBottom className={classes.typography}>
                Once the job has made its way to the front of the queue,
                a <Link href={'https://kubernetes.io/docs/concepts/workloads/controllers/job/'} target={'_blank'}>
                Kubernetes job
                </Link> is created for the pipeline. This job has four specific phases it does. Those
                phases are: clone, build, test and report. When the job reports its findings, the submission
                in the database is updated.
              </Typography>
              <Typography gutterBottom className={classes.sidebar}>
                Something new in version 2.0 is that the reporting happens while the other phases are run. This
                live reporting makes it so that students can see their results come in as they are processed instead
                of needing to wait until they are all done.
              </Typography>
              <div/>
              <BlogImg
                src={'https://anubis.osiris.services/api/public/static/f5d922b0dd893817'}
                alt={'pipeline progress gif'}
              />


              <Typography gutterBottom className={classes.typography}>
                Does any of this sound appealing to you? Reach out to us to see if Anubis is
                something that can benefit your class!
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
