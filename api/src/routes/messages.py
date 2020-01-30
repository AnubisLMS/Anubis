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

build log:
{build}

report log:
{report}
"""
