from commentaria.users.utils import profile_picture_url

context_processors = {
    "profile_picture_url": profile_picture_url
}


def import_context_processor(app):
    with app.app_context():
        @app.context_processor
        def utility_processors():
            return context_processors
