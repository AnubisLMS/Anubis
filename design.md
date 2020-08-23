# Anubis Design Doc

> Authors: John Cunnif & Somto Ejinkonye
> Version: v2.0.0

- [Overview](#overview)
    - [Elevator Pitch](#elevator-pitch)
    - [Differences from v1.0.0](differences-from-v1.0.0)
    - [Definitions](#definitions)
- [Services](#services)
    - [Traefik](#traefik)
    - [API](#api)
        - [Zones](#zones)
        - [Responsibilites](#responsibilites)
        - [SSO Authentication](#sso-authentication)
    - [Submission Pipeline](#submission-pipeline)
        - [Kube Job](#kube-job)
        - [Submission State Reporting](submission-state-reporting)
        - [Stages](#stages)
            - [Clone](#clone)
            - [Build](#build)
            - [Test](#test)
    - [Web Frontend](#web-frontend)
    - Datastores
        - Elasticsearch
        - Mariadb
    - Logging
        - logstash
- Deployment
    - Kubernetes
        - Rolling updates
        - Storage Volumes
        - Health Checks
        - Space Cluster design
    - Github
        - Organization
        - Classroom
- Using the CLI
    - Installing
    - Authenticating
    - Command cheat sheet
- Assignments
    - Creating a new Assignment
        - Writting tests
        - Uploading tests
        - Updating existing tests
        - Connecting to github classrooms
    - Getting Autograding results
    


## Overview

### Elevator Pitch

At its core, Anubis is a tool to give Intro to OS students live feedback from their homework assignments while they are working on them. Instead of having students submit a parch file, through github classrooms each student will have their own private repo for every assignment. The way students then submit their work is simply by submitting before the deadline. Students can then push, and therefore submit as many times as they would like before the deadline. 

When a student pushes to thier assignment repo, a job is launched in the Anubis cluster. That job will build their repo, run tests on the results, and store the results in the [datastore](#datastore).

Students can then navigate to the anubis website, where they will sign in through [NYU SSO](#sso). From there, they will be able to see all the current and past assignments, and submissions for their classes. They are able to view all relevent data from their build and tests for a given submission. There they can request a regrade, there by launching a new submission pipeline. While the submission still being processed, the frontend will poll the [API](#api) for updates. In this, the frontend will be containtly updating while the submission is being processed, giving a live and interactive feel to the frontend. Once a submission is processed Anubis will show the students logs from their tests, and builds along with which tests passed and which failed. 


### Differences from v1.0.0

Version 1.0.0 went through many changes over the course of the spring 2020 semester. By the end, it was stable and worked well enough. 

The places version one lacked the most was in its ability to scale. Since it was designed to run on a single server, only verticle scaling was possible. In the hour or so before the deadline for an assignment was the only time the system was stressed by the load. The server would only be able to process a limited number of submissions at a time. 

One other major issues was that github's webhook feature was not stable. It would routenly fail to deliver the webhooks to anubis indicating a new submission was pushed. This issue lead to a great deal of confusion where students could not find their submissions in the frontend because the api were never notified by github.

The primary difference in version two is scale and reliability. We are planning on displaying more meaningful feedback, with an improved UI. Along with this, we are building the new system on the container orchestrator Kubernetes. Not only does this allow us to scale horizontally significantly easier, but we will also be able to have certain guarentees about availibility of services. 


## Services

### Traefik

For our edge router, we will be using [traefik](https://docs.traefik.io/). Traefik will be what actually listens on the servers external ports. All external traffic will be routed through traefik. Above all else, we will be using Traefik's routing features to handle the Ingress of requests.

In version two of Anubis we will be using one domain, and one domain only. No subdomains. Only paths off of `anubis.osiris.services`. The way we can do this is by using some Traefik routers and middleware to route and modify incoming requests as we see them. The result of this is that we can have a single external domain with different rules, and routing depending on the destination of the domain.

| URL                                  | Services     | Requires Basic Auth |
|--------------------------------------|--------------|---------------------|
| anubis.osiris.services/api/public/*  | Public API   | no                  |
| anubis.osiris.services/api/private/* | Private API  | yes                 |
| anubis.osiris.services/kibana        | Kibana       | yes                 |
| anubis.osiris.services/*             | Web Frontend | no                  |

> The above graph shows some of the routing paths, which services they will be routed to, and if they requir [http basic auth](https://en.wikipedia.org/wiki/Basic_access_authentication).

By leveraging these features of traefik, we can make it appear that the services work different when being accessed externally. Namely the basic authentication for certin paths (and therfore services).

> One thing to note here is that when being accessed from within the cluster, none of these rules apply as we would be connecting directly to services.


### API

The API is the backbone of anubis. It is where all the heavy lifting is done. The service relys on both the [elasticsearch](#elasticsearch) and [mariadb](#mariadb) datastores to maintain state.

#### Zones

The API is split into two distinct, and uiquely treated zones. There is a `public` and a `private` zone. All endpoints for Anubis fall within one of these zones. 

These zones are simply paths that are treated differently depending on where the request is external. Namely for the private zone external requests will require http basic auth. By adding this simple level of authentication, we can lock down a section of the more sensative API to only those authenticated from the outside.

#### Responsibilities

The Anubis API is responsible for handling most basic IO, and state managing that happens on the cluster. Some of this includes: 

- Authenticating users
- Providing Class, Assignment, and Submission data to the frontend
- Handling github webhooks
- Handling reports from the submission pipeline cluster
- Handling regrade requests


#### SSO Authentication

To authenticate with the api, a token is required. The only way to get one of these tokens is through NYU Single Sign On. By doing this, we are outsourcing our authentication. This saves a whole lot of headaches while being arguably more secure that if we rolled our own.

In implementation, the when the frontend loads it will attempt to authenticate with the API. If there is a stale or broken token in the current cookies, the frontend will redirect users to the NYU login page. Given that they authenticate there, they will be redirected back to the API, where we will provide them with a token. From there, they will be logged into Anubis. 

All of this is about 20 lines on our end. All that is necessary are some keys from NYU IT.

### Submission Pipeline

#### Kube Job

A given submission pipeline is of the form of a Kubernetes [Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/). These jobs have some built in assurances. A job is configurable to continue to lanuch new containers if a Pod fails.

#### Submission State Reporting

At each and every tage of a submission pipeline, the job will report to the api with a state update. This state is in the form of a string that describes what is currently happening at that moment. This data can then be passed along to a user that is watching their pipeline be processed live.

Each unique per-assignment pipeline is packaged in the form of a docker image.
> See [Creating a new Assignment](#creating-a-new-assignment)

> An error at any stage of the submissions pipeline will result in an error being reported to the API, and the container exiting.

#### Stages

It is importaint to note that at each stage of the submission pipeline, we will be moving execution back and forth between two users. There will be the entrypoint program managing the container as user `anubis`. The `anubis` user will have much higher privaleges than the `student` user. The `student` user will be used whenever executing student code. It will not have any level of access to anything from the `anubis` user.

##### Clone

In this inital stage, we will pull the current repo down from github. After checking out the commit for the current submission, we will also delete the `.git` directory as it is not needed. Lastly we will `chown` the entire repo as `student:student`. This will then be the only place in the container that the student user can read or write to (other than /tmp of course).

##### Build

At this stage we hand execution off to student code for the first time. We will be building the student code _as the `student` user_. The command for building the container will be specified by on a per-assignment basis. The std-out of the build will be captured by the `anubis` user.

Once built, a build report will be sent to the API, along with a state update for the submission. If the student is on the submission page, then they should be see the build info shortly thereafter.

##### Test

Tests will be defined on a per-assignment basis. Again we are executing student code, as the student user.

After each test, we will return to the entrypoint program as the `anubis` user. We will then send a report of the last test before continuing to the next. 

Once we reach the last test, we send off a seperate notification to the API indicating the completion of the pipeline. It is at that point that the API marks the submission as processed.


### Web Frontend

The frontend is designed to be a simple reflection of the backend data. Once authenticated, users will be able to see the classes they are a part of, current and past assignments, and all their submissions. With few exceptions, the frontend is a near one to one translation of the API's data models. Most pages will have a corresponding API endpoint. The data shown onthat page will be in exactly the form of the API response.

The notable exceptions to this simplistic model would be the submission page, the regrade button, and the find-missing button. 

The submission page will poll for new data if the submission is not marked as processed. As it sees new data, it will update what is displayed. 

Located on the submission page, the purpose of the regrade button is to be a simple and easy way for users to request regrades. When clicked, the frontend will hit a special endpoint for requesting regrades. If successful, the submission will be re-enqueued in a submission pipeline.

On the submissions page, the find-missing button will trigger a server side update of the submission data. When the find-missing endpoint is hit, the API will use the graphql API for github to pull all the commits for all the known repos for that user. If it sees commits that were not preveously seen (likely though github not delivering a webhook), then it will create and enqueue the new submissions.




