from datetime import datetime

from anubis.utils.data import with_context
from anubis.utils.visuals.usage import get_usage_plot


@with_context
def main():
    get_usage_plot()


if __name__ == "__main__":
    print(f"Running visuals job - {datetime.now()}")
    main()
