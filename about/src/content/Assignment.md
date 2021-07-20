---
title: How Assignments Work In Anubis  
slug: packaging 
date: 2021-07-08 
author: John Cunniff
description: Assignment in Anubis work unlike any other homework solution. In most college classes, when students finish their work, they turn in a final copy into the professor. With Anubis, we eliminate this process by making it so that students turn in their homework simply by working on it. 
published: true
---
Assignment in Anubis work unlike any other homework solution. In most college classes,
when students finish their work, they turn in a final copy into the professor. With Anubis,
we eliminate this process by making it so that students turn in their homework simply by
working on it.

#### Assignment Structure

Each student will get their very own private repository on github that is created from an
assignment template. With this repository, students can work on their homework and submit by
pushing to their repo. The Anubis servers track the repos and launch &quot;submission pipelines&quot;
for each push. *More on that later...*

This process is designed to be seamless. The only thing students need to do is enter their github
username into Anubis at the beginning of the semester. The student&apos;s github username, not their
netid
is tied to the repo. For this, we need to be able to match the student&apos;s github username to their
NYU netid.


#### Submission Pipelines

You may be now asking yourself what exactly submission pipelines are. They are the processes that
actually do the autograding tests. These pipelines have evolved and changed greatly since Anubis
version 1.0 and are complex multi stage jobs.

![submission flow svg](/api/public/static/b88665d8c43989e0)

Github first reports a push to the Anubis api by a webhook. At this point, the submission
is registered. This is
the first time Anubis can account for this work, so it is this time that is counted as the time of
submission.

 > I point out the submission times because we could have just trusted the git repo commit times and used
those for the time of submission. But as you could probably guess commit timestamps are trivially easy
to fake.

With the submission accounted for, a submission pipeline job is enqueued in the RPC queue. The
reason for the queue is that there may be times when we actually have more submissions that need
to be run than can be run at a single time. By forcing jobs to go into a queue, we can set artificial
limits on how many submission pipelines can be run at a single time. While students are working
these limits are almost never reached, but imagine we need to regrade all the submissions for
an assignment at once. Some assignments can get up to 3000 submissions. We then really need to
queue up the pipelines so only some number are run at a single time.