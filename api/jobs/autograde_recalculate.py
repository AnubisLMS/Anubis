import json
from datetime import datetime, timedelta

from anubis.lms.autograde import bulk_autograde
from anubis.models import (
    Assignment,
)
from anubis.utils.config import get_config_int
from anubis.utils.data import with_context


def autograde_recalculate():
    """
    Calculate stats for recent submissions

    :return:
    """

    autograde_recalculate_days = get_config_int('AUTOGRADE_RECALCULATE_DAYS', default=60)
    autograde_recalculate_duration = timedelta(days=autograde_recalculate_days)

    recent_assignments = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date > datetime.now() - autograde_recalculate_duration,
    ).all()

    print(json.dumps({
        'autograde recalculate assignments:': [assignment.data for assignment in recent_assignments]
    }, indent=2))

    for assignment in recent_assignments:
        bulk_autograde(assignment.id)


@with_context
def reap():
    autograde_recalculate()


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
