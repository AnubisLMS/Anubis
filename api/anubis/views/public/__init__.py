def register_public_views(app):
    from anubis.views.public.auth import auth
    from anubis.views.public.ide import ide
    from anubis.views.public.repos import repos
    from anubis.views.public.webhook import webhook
    from anubis.views.public.profile import profile
    from anubis.views.public.submissions import submissions
    from anubis.views.public.assignments import assignments
    from anubis.views.public.static import static

    views = [
        auth, ide, repos, webhook, profile,
        submissions, assignments, static
    ]

    for view in views:
        app.register_blueprint(view)
