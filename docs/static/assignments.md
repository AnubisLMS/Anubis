# Assignments

The basic flow for an assignment is as follows:

- The student will click on a link from github classroom that will fork a template repo into the github org.
This forked repo should be private to the student and the TAs. If the repo is public, then students will
be able to see each others work, rendering the entire assignment worthless.
- Students will then work on the assignment, making and committing necessary changes. When they want to submit,
they will push to the repo. This push should trigger a webhook in the github org that will trigger a submission
job.
- The student can then navigate to the Anubis website in their browser. There they can enter the commit hash they 
submitted, along with the their netid. They will then be presented with a live and interactive interface for viewing,
and interacting with their submission. They will be able to see live updates of their submission, and be able
to request regrades.

## Github org configuration
The github org that the classroom is built on must have a webhook defined for pushes. This webhook should
be reporting to the /public/webhook endpoint in the api. Without this defined, Anubis is blind to submissions.

## Adding an assignment

There are a couple moving pieces to an assigment. If any of the pieces are missing, then you
will run into errors somewhere. For this, I **strongly** encourage you to test assignments 
before releasing them. This means making sure the test scripts work, and making sure that when 
you push to an assignment repo, that the job is triggered, and executed correctly. This process 
works much more fluidly when you have a fully working solution to your assignment. I can not stress
this enough: do not assume that the tests just work, you have to test the test scripts against the
plain template repos, and a full solution repo. You must also test to make sure that the assignment builds,
and runs in the student VMs.

1. Create a template. Here you should make a template repo that has anything you will need for the student,
or for testing. For xv6 assignments, this means making a copy of the current xv6 repo and making any necessary 
changes for the assignment.
2. Write tests. You should refer to the tests that have already been written to see how to parse qemu 
output and save results. The basic gist of it is that you should design your assignments to be able to accept some
randomized input for a then calculated expected output. Your tests should supply programs with randomized input and
compare the output against what was expected.

