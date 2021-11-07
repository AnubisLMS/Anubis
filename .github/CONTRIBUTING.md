# Contributing to Anubis

1. [Descriptive Suffixes](#descriptive-suffixes)
2. [Commit Message Guidelines](#commit-message-guidelines)
3. [Issues](#issues)
4. [Pull Requests](#pull-requests)
5. [Code Style](#code-style)

## Descriptive Suffixes

All Pull Requests should begin with one of our descriptive suffixes:
- FIX fix of something
- CHG change to somthing
- RM removal of something
- ADD addition of somthing

Similarly for issues:
- BUG bug report
- QSN question about Anubis
- FIX fix of something
- CHG change to somthing
- RM removal of something
- ADD addition of somthing

## Commit Message Guidelines

For all commits please begin them with an all caps descriptive suffix from the above. The rest of the commit message
should be lowercase.

Examples:
```
git commit -m "FIX issue with this thing"
git commit -m "CHG move function to this file"
git commit -m "RM unneeded file"
git commit -m "ADD something new"
```

## Issues

Before posting a new issue, please make sure that you explain what the purpose of the issue is. The more information you give, the faster we will be able to help.

If you are reporting a bug or some other issue then please provide steps to reproduce. If you are developing, then providing your environment will be quite helpful (Operating System, debug environment, etc.). Screenshots are very helpful!

Please make sure your issue title starts with an all caps descriptive suffix from above.

## Pull Requests

If you are submitting a Pull Request, thank you for contributing! Please check for and link any open Issues that may be relevant to the PR. Also add any labels that may be relevant. 

Please make sure that your changes are clearly described in the description of the PR. This will help the maintainers understand and speed up the review and merging process.

Please make sure your PR title starts with an all caps descriptive suffix from above.


## Code Style

We use several lint tools to keep our code style consistent.

For the frontend, we use [eslint](https://eslint.org/), yet we are not super strict about that.

For the backend, we use [black](https://black.readthedocs.io/en/stable/index.html) and [isort](https://pycqa.github.io/isort/). Please make sure that you run `make lint` in the `/api` directory before committing your changes.

## Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

 (a) The contribution was created in whole or in part by me and I
     have the right to submit it under the open source license
     indicated in the file; or

 (b) The contribution is based upon previous work that, to the best
     of my knowledge, is covered under an appropriate open source
     license and I have the right under that license to submit that
     work with modifications, whether created in whole or in part
     by me, under the same open source license (unless I am
     permitted to submit under a different license), as indicated
     in the file; or

 (c) The contribution was provided directly to me by some other
     person who certified (a), (b) or (c) and I have not modified
     it.

 (d) I understand and agree that this project and the contribution
     are public and that a record of the contribution (including all
     personal information I submit with it, including my sign-off) is
     maintained indefinitely and may be redistributed consistent with
     this project or the open source license(s) involved.
