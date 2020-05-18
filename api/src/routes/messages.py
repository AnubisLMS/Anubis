crit_err_msg = """
There was an unexpected and critical error in grading your recent OS3224 submission.
The admins for the autograding cluster have been notified of this error.

netid: {netid}
assignment: {assignment}
commit: {commit}
"""

err_msg = """
There was an error in grading your recent OS3224 submission.

netid: {netid}
assignment: {assignment}
commit: {commit}

{error}
"""

success_msg = """
Your recent submission for OS3224 was processed.

netid: {netid}
assignment: {assignment}
commit: {commit}

report:
{report}

build log:
{build}

test logs:
{test_logs}
"""


code_msg = """

Hello {name},

Here is your Anubis code for your upcoming OS exam. Don't worry, there is nothing you need to do right 
now. This it just so you can access your materials come test day. Try not to lose this!

{code}

Good luck,
John 

"""