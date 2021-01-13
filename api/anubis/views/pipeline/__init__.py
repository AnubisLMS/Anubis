def register_pipeline_views(app):
    from anubis.views.pipeline import pipeline

    views = [
        pipeline,
    ]

    for view in views:
        app.register_blueprint(view)
