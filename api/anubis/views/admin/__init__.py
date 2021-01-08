def register_admin_views(app):
    from anubis.views.admin.ide import ide
    from anubis.views.admin.auth import auth
    from anubis.views.admin.assignments import assignments
    from anubis.views.admin.seed import seed
    from anubis.views.admin.questions import questions
    from anubis.views.admin.regrade import regrade
    from anubis.views.admin.stats import stats
    from anubis.views.admin.static import static

    views = [
        ide, auth, assignments, seed,
        questions, regrade, stats, static
    ]

    for view in views:
        app.register_blueprint(view)
