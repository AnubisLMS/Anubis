from flask import Flask


def add_healthcheck(app: Flask):
    from anubis.utils.http.decorators import json_response
    from anubis.models import Config
    from anubis.utils.cache import cache_health

    @app.route("/")
    @json_response
    def index():
        status_code = 200
        status = {
            'db': 'Healthy',
            'cache': 'Healthy',
        }

        try:
            Config.query.all()
        except:
            status['db'] = 'Unhealthy'
            status_code = 500

        try:
            cache_health()
        except:
            status['cache'] = 'Unhealthy'
            status_code = 500

        return status, status_code
