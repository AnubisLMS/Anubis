# Jobs

Using the [rq](https://python-rq.org/) library, we can enqueue jobs that will be handled asynchronously by workers.
This library requires that the jobs be defined as a callable function and arguments for it (in a tuple).
We need this callable function to be in scope for both the job enqueuer, and the workers.
Because of this constraint, we have this seperate directory where jobs can be defined. 
