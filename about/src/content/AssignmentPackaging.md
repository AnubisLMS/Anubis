---
title: Assignment Packaging
slug: assignment-packaging
date: 2021-03-24
author: John Cunniff
description: Assignment in Anubis work unlike any other homework solution. In most college classes, when students finish their work, they turn in a final copy into the professor. With Anubis, we eliminate this process by making it so that students turn in their homework simply by working on it.
published: true
---

One of the largest systems to get a major overhaul in between
version 1 and version 2 was the way that assignment tests are
packaged. In the original version, tests were a bit of a free
for all.

#### Version 1 to Version 2

Eventually some standard functions were added so that
we could save and store the autograding results, but the testing
itself was still inconsistent. We were essentially re-writing all the
code to run the student&apos;s xv6, then parse the output for each
assignment. Parsing issues that came up would be fixed incrementally
from assignment to assignment until we had something semi-stable
by the last assignment.

For version 2 we needed better packaging of the assignment tests.
There are two main improvements that made this change work.

- Assignment Templating
- Standardizing API and parsing

Each assignment is packaged essentially as a docker image. The
image has the metadata for the assignment, the tests specific for
that assignment, along with the standard autograding
API and parsing modules.

#### Creating a new assignment

Using the Anubis CLI, you can run one quick command to get
your very own assignment template.

![demo assignment](/api/public/static/b176c707620f500b)

The meta.yaml file is where you give the assignment a name
and set its release and due dates. You can also set your assignment to be
hidden from student or not. If the assignment is not hidden, then it
will become visible to students after the release date. Something to note
is that these timestamps are interpreted as **America/New_York**.
Anubis was first developed before coronavirus made everything remote,
so it did not make sense to have timestamps be interpreted as a more
international friendly format like UTC.

![demo assignment](/api/public/static/dcf6dc895dcb75f2)

#### Writing Tests

The build and test code is all in assingment.py from the generated
template. There is not actually much code that needs to change from
assignment to assignment. The only thing that changes is how the
output is interpreted. For the most part it falls into having some
form of randomized input and comparing the actual output to an
expected output.

Let&apos;s work on an example from the midterm this semester.
Students were required to implement a sed program. The sed program
that they implemented was significantly more simple than the actual
gnu sed program from coreutils. Their sed program just needed to find
and replace 3 characters from a file and print it to screen. This
format is perfect for setting up randomized input, and expected output.
All we need to do is generate a file and compile it into xv6, then
run the student&apos;s xv6 and the sed included in coreutils and
compare the two outputs.

#### Building

![demo build](/api/public/static/243d6d28714e96f5)

> To let anubis know that this is the build function, we simply decorate it with `@register_build`.

The build is pretty simple for this assignment. We use a
lorem ipsum generator library to fill in a file text.txt with
a few sentences separated by newlines. This will make it so that
each time this is run, we should get a relatively random text.txt.
This fulfills our randomized input requirement.

Once our input file is generated, we can build the student xv6
and report the stdout and build status. We communicate back to
Anubis by setting the values of the stdout and passed fields in
a build_result object passed to the build function.

#### Tests

![demo tests](/api/public/static/14da736d560a86e6)

We then run both the student sed, and coretuils sed and compare the results.
The functions xv6_run, exec_as_student, did_xv6_crash and verify_expected
are all standard Anubis autograding library functions. Formalizing these
functions is what makes writing these tests so easy. We&apos;re simply
getting the student output, and the expected output and letting the anubis
standard functions handle the rest. As long as we handle these steps
autograding is easy!

#### Deploying

Sending the assignment off to Anubis is very simple. All we need to
do is first send the metadata to the Anubis API, then build and
push the autograding image.

![demo sync](/api/public/static/ee0d3c5a5684fa68)
![demo push](/api/public/static/71f11b54ad2e38f4)
