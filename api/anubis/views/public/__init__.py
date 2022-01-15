def register_public_views(app):
    from anubis.views.public.assignments import assignments
    from anubis.views.public.auth import auth_, github_oauth_, nyu_oauth_
    from anubis.views.public.courses import courses_
    from anubis.views.public.ide import ide_
    from anubis.views.public.lectures import lectures_
    from anubis.views.public.memes import memes
    from anubis.views.public.profile import profile
    from anubis.views.public.questions import questions
    from anubis.views.public.repos import repos_
    from anubis.views.public.static import static
    from anubis.views.public.submissions import submissions_
    from anubis.views.public.visuals import visuals
    from anubis.views.public.webhook import webhook
    from anubis.views.public.playgrounds import playgrounds_
    from anubis.views.public.forums import forums_

    views = [
        auth_,
        nyu_oauth_,
        github_oauth_,
        ide_,
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
        playgrounds_,
        forums_,
    ]

    for view in views:
        app.register_blueprint(view)
