# Services

## API

The entire api is split into two basic 'zones'. There is a public and a private zone. The public zone will be accessable externally,
meaning that anyone will be able to hit those routes. The private zone is freely accessable to the internal services, but requires 
http basic auth to be accessed externally.

### Public Zone Routes

1. /public/webhook
  - This route should be hit by the github when a push happens. 
  We should take the the github repo url and enqueue it as a job in the
  Redis queue.

2. /public/submissions/<commit>/<netid>
  - This route should gather all the data we have about the submission corresponding to that
  commit hash and netid. This route should only be hit when the student is using the anubis
  website. Since this is a route that has database IO, there is some light caching of the 
  responses.
  - Errors returned from this endpoint are purposefully
  ambiguous.

3. /public/regrade/<commit>/<netid>
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
  
9. /private/stats/<assignment_name>/<netid>
  - Stats are considered to be the results that anubis pumps out. This means that this endpoint is
  used when TA's that are grading to see if their student's tests passed or failed. This route has
  the potential to be extremely IO intensive, so there is heavy caching of the responses.
  - This route should only ever be used by the cli.

## Redis Cache
## Mysql Database
## Worker Pool
## SMTP Server
## Elasticsearch / Kibana
## Anubis Website
