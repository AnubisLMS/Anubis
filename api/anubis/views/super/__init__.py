def register_super_views(app):
    from anubis.views.super.config import config_
    from anubis.views.super.ide import ide_
    from anubis.views.super.playgrounds import playgrounds_
    from anubis.views.super.students import students_
    from anubis.views.super.email import email_

    views = [
        ide_,
        config_,
        playgrounds_,
        students_,
        email_,
    ]

    for view in views:
        app.register_blueprint(view)
