from anubis.utils.visuals.usage import get_usage_plot


def create_visuals(*_, **__):
    """
    Create visuals files to be cached in redis.

    :return:
    """
    from anubis.app import create_app
    app = create_app()

    with app.app_context():
        with app.test_request_context():
            get_usage_plot()
