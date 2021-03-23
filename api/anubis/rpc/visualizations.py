from anubis.utils.visualizations import get_usage_plot


def create_visuals():
    """
    Create visuals files to be cached in redis.

    :return:
    """
    from anubis.app import create_app
    app = create_app()

    with app.app_context():
        get_usage_plot()
