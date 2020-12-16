from flask import has_request_context
from datetime import datetime, timedelta
from anubis.app import create_app
from anubis.models import db, Submission, Assignment, TheiaSession
from anubis.utils.students import bulk_stats
from anubis.utils.redis_queue import enqueue_ide_stop, enqueue_ide_reap_stale
from sqlalchemy import func, and_
import json


def reap_stale_submissions():
    """
    This will set find stale submission and set them to processed. A stale
    submission is one that has not been updated in 15 minutes and is still
    in a processing state.

    Flask app context is required before calling this function.

    :return:
    """

    print("Reaping stale submissions")

    # Find and update stale submissions
    Submission.query.filter(
        Submission.last_updated < datetime.now() - timedelta(minutes=15),
        Submission.processed == False
    ).update({
        Submission.processed: True,
        Submission.state: "Reaped after timeout"
    }, False)

    # Commit any changes
    db.session.commit()

    print("")


def reap_theia_sessions():
    # Get theia sessions that are older than n hours
    theia_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.last_proxy <= datetime.now() - timedelta(hours=3),
    ).all()

    for theia_session in theia_sessions:
        enqueue_ide_stop(theia_session.id)


def reap_stats():
    """
    Calculate stats for recent submissions

    :return:
    """
    recent_assignments = Assignment.query.group_by(
        Assignment.class_id
    ).having(
        and_(
            Assignment.release_date == func.max(Assignment.release_date),
            Assignment.release_date > datetime.now() - timedelta(days=60),
        )
    ).all()

    print(json.dumps({
        'reaping assignments:': [assignment.data for assignment in recent_assignments]
    }, indent=2))

    for assignment in recent_assignments:
        bulk_stats(assignment.id)


def reap():
    app = create_app()

    with app.app_context():
        # Reap the stale submissions
        reap_stale_submissions()
        enqueue_ide_reap_stale()

        with app.test_request_context():
            # Calculate bulk stats (pre-process stats calls)
            reap_stats()


if __name__ == "__main__":
    print("")
    print("""
             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

""")
    reap()
