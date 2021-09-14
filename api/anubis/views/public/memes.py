from flask import Blueprint, redirect

from anubis.utils.logging import logger

memes = Blueprint("public-memes", __name__, url_prefix="/public/memes")


@memes.route("/")
def public_memes():
    """
    There are a couple of places on the front end that have
    hidden rick rolls. They link to this endpoint where they will
    be redirected to the youtube rick roll video.

    :return:
    """

    # Log the rick roll
    logger.info("rick-roll")

    # Redirect them to the rick roll video
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1")
