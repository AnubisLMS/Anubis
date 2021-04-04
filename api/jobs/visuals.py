from datetime import datetime

from anubis.app import create_app
from anubis.utils.visualizations import get_usage_plot


def main():
    app = create_app()

    with app.app_context():
        with app.test_request_context():

            # Create and cache the usage plot
            get_usage_plot()


if __name__ == "__main__":
    print(f"Running visuals job - {datetime.now()}")
    main()
