from flask import Blueprint, redirect

from anubis.utils.services.elastic import log_endpoint
from anubis.utils.services.logger import logger

memes = Blueprint("public-memes", __name__, url_prefix="/public/memes")


@memes.route("/")
@log_endpoint("rick-roll", lambda: "rick-roll")
def public_memes():
    logger.info("rick-roll")
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1")
