def register_public_views(app):
    from anubis.views.public.auth import auth_
    from anubis.views.public.auth import oauth_
    from anubis.views.public.ide import ide
    from anubis.views.public.repos import repos_
    from anubis.views.public.webhook import webhook
    from anubis.views.public.profile import profile
    from anubis.views.public.submissions import submissions_
    from anubis.views.public.assignments import assignments
    from anubis.views.public.static import static
    from anubis.views.public.courses import courses_
    from anubis.views.public.questions import questions
    from anubis.views.public.memes import memes
    from anubis.views.public.visuals import visuals
    from anubis.views.public.lectures import lectures_

    views = [
        auth_,
        oauth_,
        ide,
        repos_,
        webhook,
        profile,
        submissions_,
        assignments,
        static,
        courses_,
        questions,
        memes,
        visuals,
        lectures_,
    ]

    for view in views:
        app.register_blueprint(view)
