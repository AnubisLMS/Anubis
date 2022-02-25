from typing import List

from flask import Blueprint

from anubis.models import db, TheiaImage, TheiaImageTag
from anubis.utils.auth.http import require_superuser
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_endpoint, json_response, load_from_id

ide_ = Blueprint("super-ide", __name__, url_prefix="/super/ide")


@ide_.get("/images/list")
@require_superuser()
@json_response
def super_ide_images_list():
    images: List[TheiaImage] = TheiaImage.query.all()

    return success_response({"images": [image.data for image in images]})


@ide_.post("/images/save")
@require_superuser()
@json_endpoint([("images", list)])
def super_ide_images_save(images: list):
    for image in images:
        image_db: TheiaImage = TheiaImage.query.filter(
            TheiaImage.id == image["id"],
        ).first()

        if image_db is None:
            continue

        for field, value in image.items():
            if field in image_db.__table__.columns:
                if isinstance(value, str):
                    value = value.strip()
                setattr(image_db, field, value)

        for tag in image["tags"]:
            theia_image_tag_db: TheiaImageTag = TheiaImageTag.query.filter(TheiaImageTag.id == tag["id"]).first()
            for field, value in tag.items():
                if isinstance(value, str):
                    value = value.strip()
                setattr(theia_image_tag_db, field, value)

    db.session.commit()

    images: List[TheiaImage] = TheiaImage.query.populate_existing().all()
    return success_response(
        {
            "images": [image.data for image in images],
            "status": "Images saved",
        }
    )


@ide_.post("/images/new")
@require_superuser()
@json_response
def super_ide_images_new():
    image_db = TheiaImage(
        image="registry.digitalocean.com/anubis/theia-xv6",
        title="theia-xv6",
        description="theia-xv6",
        icon="",
        public=False,
    )

    db.session.add(image_db)
    db.session.commit()

    images: List[TheiaImage] = TheiaImage.query.all()
    return success_response(
        {
            "images": [image.data for image in images],
            "status": "Image reference created",
        }
    )


@ide_.post("/image-tags/new/<string:id>")
@require_superuser()
@load_from_id(TheiaImage)
@json_response
def super_ide_image_tags_new(theia_image: TheiaImage):
    image_tag_db = TheiaImageTag(
        image_id=theia_image.id,
        tag="latest",
        title="latest",
        description="",
    )

    db.session.add(image_tag_db)
    db.session.commit()

    images: List[TheiaImage] = TheiaImage.query.all()
    return success_response(
        {
            "images": [image.data for image in images],
            "status": "Image Tag reference created",
        }
    )


@ide_.delete("/image-tags/delete/<string:id>")
@require_superuser()
@load_from_id(TheiaImageTag)
@json_response
def super_ide_image_tags_delete(theia_image_tag: TheiaImageTag):
    db.session.delete(theia_image_tag)
    db.session.commit()

    images: List[TheiaImage] = TheiaImage.query.all()
    return success_response(
        {"images": [image.data for image in images], "status": "Image Tag reference deleted", "variant": "warning"}
    )
