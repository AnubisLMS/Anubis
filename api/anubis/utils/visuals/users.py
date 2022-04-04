from datetime import datetime, timedelta

from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job
from anubis.utils.usage.users import get_platform_users
from anubis.utils.visuals.files import convert_fig_bytes
from anubis.utils.visuals.watermark import add_watermark


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_platform_users_plot(days: int, step: int = 1):
    import matplotlib.pyplot as plt

    now = datetime.now().replace(hour=0, second=0, microsecond=0)
    start_datetime = now - timedelta(days=days - 1)

    xx = []
    yy = []

    fig, ax = plt.subplots(figsize=(12, 10))

    for n in range(0, days, step):
        day = start_datetime + timedelta(days=n)
        y = get_platform_users(day)

        xx.append(day)
        yy.append(y)

    ax.plot(xx, yy, 'b--', label='Total users registered on platform')

    ax.legend(loc='upper left')
    ax.grid()
    ax.set(
        title='Total users registered on Anubis LMS over time',
        xlabel='Time',
        ylabel='Registered Users',
    )
    # set y max to the nearest hundred
    ax.set_ylim([0, ((yy[-1] // 100) + 1) * 100])
    add_watermark(ax)

    return convert_fig_bytes(plt, fig)
