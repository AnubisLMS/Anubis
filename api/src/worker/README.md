# Jobs

Using the [rq](https://python-rq.org/) library, we can enqueue jobs that will be handled asynchronously by workers.
This library requires that the jobs be defined as a callable function and arguments for it (in a tuple).
We need this callable function to be in scope for both the job enqueuer, and the workers.
Because of this constraint, we have this seperate directory where jobs can be defined. 

The rq-worker nodes all have the docker socket mounted, and can therefore interface with
docker directly.

# Test Job Pipeline

The process for testing should be in four cycles. Each one is handled in a seperate
docker container that has specific permissions. We must be very careful for this
section of the cluster, as we are quite literally executing student code. This
is the primary reason we split the testing into mutiple phases in multiple container.
The four cycles are:

```
- clone
- build
- test
- report
```

### clone
The clone phase does exactly what it sounds like. It just clones the repo to /mnt/submission/xv6-public

**This container has networking capabilities. It is not placed on the traefik-proxy network.**

### build
This container does the build of xv6. This is the most criticle point in the entire cluster, since
we are directly executing student code in the build container. Because of this, we must take extra care
to strip these containers of unnecessary permissions. We want to make sure that even if a student puts
something potentially malicous in their code, they would not be able to say, beacon or phone home. This
containers only IO should be through the volume.

**This container does __not__ have networking capabilities**

### test
The test containers run the per assignment tests, and drop json files documenting the test results in
the shared volume directory..

**This container does __not__ have networking. This container runs in privileged mode for KVM**

### report
This step just compiles the report jsons and sends them to the api for logging and reporting back to the user.
The reason this step is in a seperate container is because I don't feel comfortable giving any phase of
the test cyle privileged mode and networking. This container is also on the proxy network so it can
connect to an api node. This means this container could feasably connect to any of the other services.

**This container has networking. This container is on the traefik-proxy network**

# Notes

Each container must have a shared workspace, so we can transfer files between them.
To hanle this, we first create a docker volume for the submission. That docker
volume is managed by docker, not us, so we need not worry about its place on disk.
That volume will be mounted to /mnt/submission in each container.


TODO re-document this whole procedure.
TODO add timeouts to prevent a stale worker

