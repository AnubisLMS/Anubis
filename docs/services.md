# Services

## API

The entire api is split into two basic 'zones'. There is a public and a private zone. The public zone will be accessable externally,
meaning that anyone will be able to hit those routes. The private zone is freely accessible to the internal services, but requires 
http basic auth to be accessed externally.

### Public Zone Routes

1. /public/webhook
  - This route should be hit by the github when a push happens. 
  We should take the the github repo url and enqueue it as a job in the
  Redis queue.

2. /public/submissions/:commit/:netid
  - This route should gather all the data we have about the submission corresponding to that
  commit hash and netid. This route should only be hit when the student is using the anubis
  website. Since this is a route that has database IO, there is some light caching of the 
  responses.
  - Errors returned from this endpoint are purposefully
  ambiguous.

3. /public/regrade/:commit/:netid
  - When a student clicks the regrade button in the website, this route should get hit with
  the commit and netid of the submission. If the commit hash and netid are valid, then the
  metadata and corresponding objects are reset, and the job is re-enqueued. 
  - Errors returned from this endpoint are purposefully
  ambiguous.

### Private Zone Routes

1. /private/report-panic
  - A panic in anubis is defined to be an error that was not expected, handled, or otherwise
  accounted for. This route should only ever be hit when there is a panic reported from a 
  service in the cluster. The error will be logged in the mysql database, elasticsearch and
  an email will be sent to admins.

2. /private/report-error
  - An error in anubis is defined to be an exception that was handled. The most common things 
  here will be build errors or testing errors. The tests are not perfect, and if someone is doing
  something that does not make sense, the tests may crash. This is where those errors will be 
  reported. There is no need to notify admins when this route / when an error occurs.

3. /private/report
  - This endpoint will be hit whenever a worker in the worker pool finishes the testing pipeline
  and needs to report its results. The specifics of the structure of the report are documented in
  the route itself.

4. /private/ls
  - This endpoint will return a json containing all the submissions that are currently in a processing
  state. That means submissions that are currently either enqueued, or running.
  - This endpoint is used by the anubis cli.

5. /private/dangling
  - A dangling submission is when a student submits pushes to a repo, but we don't have their netid.
  This will create a submission where we know the github username, but the job will be held in limbo
  until the student's github username is added to the database.
  - This endpoint is used by the anubis cli.

6. /private/restart
  - Restarting a job using the cli will hit this endpoint to re-enqueue the job.
  - This endpoint was built before there was a website with a regrade button, and doesn't serve
  much of a purpose anymore. 
  - This endpoint is used by the anubis cli.

7. /private/fix-dangling
  - When this route is hit, it will attempt to look at dangling submissions, and match github usernames
  to netid's. If any matches are found, the submissions meta will be updated and enqueued as jobs.
  - This endpoint is used by the anubis cli.

8. /private/assignment
  - This route is a catchall endpoint for creating, modifying or listing assignment data.
  - This endpoint should only ever be hit by the cli.
  
9. /private/stats/:assignment_name/:netid
  - Stats are considered to be the results that anubis pumps out. This means that this endpoint is
  used when TA's that are grading to see if their student's tests passed or failed. This route has
  the potential to be extremely IO intensive, so there is heavy caching of the responses.
  - This route should only ever be used by the cli.

## Redis Cache

This service operates with no configuration. It is used to cache some endpoints responses. It is 
primarily used by the [python-rq](https://python-rq.org/) library as a job queue. Redis's storage
is volatile, meaning that when it it restarted, all cached entries / the job queue is lost. Be 
mindful of this when you deploy.

## Mysql Database

The Mysql database is used to store information about the students, submissions, builds, 
test results, and errors. There should be no configuration necessary to launch this service.

*Any and all timestamps recorded in the database will be America/New_York timestamps.*
*Check the models.py file in the api for a full description of the different tables.*

## Worker Pool

The worker pool is a cluster of worker services. These services connect to redis, dequeue and
run jobs. There is nothing else they do. These jobs are individual submission pipelines. The pipelines
have 4 distinct stages that each run in their own docker container. These containers have very
specific permissions at each stage. 

For each submission job, there is a docker volume that is created that is shared between the 
containers. This is how input / output is transferred between containers.

1. Clone
  - At this stage, the repo is cloned into the shared volume. The container will mount 
  `/root/.ssh` in order to use the root ssh keys. Please make sure that there is an ssh 
  key that is there that has access to student repos. You will also need a ssh config file
  with an entry defined for github.
  - This container will have internet
  
2. Build
  - At this stage, we will actually build whatever we need for the tests. In the build.py
  file in the api, there are specific filename arguments that are specified for each assignment.
  Those filenames will should be makefile targets in the repo. The build container will attempt
  to make those targets.
  - Failures at this stage will be the most common error in the pipeline. An error at this stage
  will prompt an error report being sent to the api, and the submission being marked as processed.
  - This container will **NOT** have internet.

3. Test
  - The test stage is where the compiled programs will be run and their output will be parsed 
  and checked against expected output. Ideally these tests will be made so that some randomized 
  input will be given to the program and the output should be compared against a calculated 
  expected output. The parsing for these tests should be implemented loosely. The tests at this
  stage should just be python scripts that call and parse processes like qemu for output.
  - When tests finish, they should call functions in `api/assignments/assignments/utils.py`
  for saving test reports. These reports will be saved as json's in the shared volume.
  - Errors at this stage should **NOT** be reported to students. In the event that a student 
  attempts to attack Anubis, giving output at this stage would be making it easy.
  - This container will **NOT** have any networking capabilities.
  
4. Report
  - Using the report json's from the test phase, this stage will read all those reports and send 
  them to the api. It is **EXTREMELY** important that this remains a separate phase entirely. This
  container having access to the internal docker network (and other services) makes it a critical 
  point in the build pipeline. If a student was able to manipulate this phase, they could potentially
  have access to the entire cluster. That is why this phase just reads the json files and reports 
  them to the api.
  - This container has networking capabilities, and resides on the internal docker network. (ie. 
  it can communicate with the api and other services)

## SMTP Server

Nothing much going on here. This is simply a simple smtp server that will send out emails to admins
when there is a panic. 

Before there was a website for students to view their submissions, we had issues with emails being
blocked by spam filters. For this, we should use emails very sparingly to avoid being blacklisted. 

## Elasticsearch / Kibana

Elasticsearch is a database and a search engine. Kibana is a web frontend for viewing elasticsearch data.
Anubis uses elasticsearch for log aggregation, tracking, and telemetry. All requests that are 
submitted to Anubis are geo located, and logged in elasticsearch. This data is then used by kibana
for making dashboards and debugging. The kibana dashboard is externally accessible (with a username
password).

## Anubis Website

The website is a react frontend for viewing submission data. It should be used by students to view the 
status of their submissions. When the page loads, they will be prompted to enter the commit hash, then 
their netid to view the submission data. This is very much an honor code. Students could in theory put 
other students commit hashes and netides into the website to view each others submissions. Though this would
require the students to be sharing their submissions / repos with other students. It should be made clear 
to students that attempting to view others submissions is an act of academic dishonesty and will be treated 
as such. Telemetry is built into the website. This means that we will have maps in kibana that show dots 
for the approximate locations of students. This should make it simple for finding potential cheaters.
