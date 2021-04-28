def register_admin_views(app):
    from anubis.views.admin.ide import ide
    from anubis.views.admin.auth import auth
    from anubis.views.admin.assignments import assignments
    from anubis.views.admin.seed import seed
    from anubis.views.admin.questions import questions
    from anubis.views.admin.regrade import regrade
    from anubis.views.admin.autograde import autograde_
    from anubis.views.admin.static import static
    from anubis.views.admin.users import students
    from anubis.views.admin.courses import courses_
    from anubis.views.admin.config import config_
    from anubis.views.admin.visuals import visuals_

    views = [
        ide,
        auth,
        assignments,
        seed,
        questions,
        regrade,
        autograde_,
        static,
        students,
        courses_,
        config_,
        visuals_,
    ]

    for view in views:
        app.register_blueprint(view)
