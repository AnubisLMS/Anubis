from datetime import datetime

from dateutil.parser import parse as date_parse
from flask import Blueprint, request

from anubis.lms.courses import assert_course_context, course_context
from anubis.models import LectureNotes, db
from anubis.utils.auth.http import require_admin
from anubis.utils.data import req_assert
from anubis.utils.http import get_request_file_stream, success_response
from anubis.utils.http.decorators import json_response
from anubis.utils.http.files import get_mime_type, process_file_upload

lectures_ = Blueprint("admin-lectures", __name__, url_prefix="/admin/lectures")


@lectures_.get("/list")
@require_admin()
@json_response
def admin_static_lectures_list():
    """
    List all lecture notes for the course

    /admin/lecture/list

    :return:
    """

    # Build Query. Defer the blob field so
    # it is not loaded.
    query = LectureNotes.query.filter(LectureNotes.course_id == course_context.id).order_by(
        LectureNotes.post_time.desc()
    )

    # Get all public static files within this course
    lectures = query.all()

    # Pass back the list of files
    return success_response({"lectures": [lecture.data for lecture in lectures]})


@lectures_.get("/delete/<string:lecture_notes_id>")
@require_admin()
@json_response
def admin_lecture_delete_lecture_id(lecture_notes_id: str):
    """
    Delete a course lecture notes.

    :param lecture_notes_id:
    :return:
    """

    # Get lecture notes
    lecture_notes = LectureNotes.query.filter(
        LectureNotes.id == lecture_notes_id,
        LectureNotes.course_id == course_context.id,
    ).first()

    # Assert that the static file is within the current course context
    assert_course_context(lecture_notes)

    # Make sure we got one
    req_assert(lecture_notes is not None, message="Lecture notes not found")

    # Mark the notes for deletion
    db.session.delete(lecture_notes)

    # Commit the delete
    db.session.commit()

    return success_response(
        {
            "status": "Lecture Notes deleted",
            "variant": "warning",
        }
    )


@lectures_.post("/save/<string:lecture_notes_id>")
@require_admin(unless_debug=True)
@json_response
def admin_lecture_save(lecture_notes_id: str):
    """
    Update an existing lecture notes object. Change the
    lecture number, title or description.

    body = {
      number: 0,
      title: 'this is the title',
      description: 'this is the description',
    }

    :return:
    """

    # Get fields from params
    post_time = request.args.get("post_time", default=None)
    title = request.args.get("title", default="")
    description = request.args.get("description", default="")

    # If post time was in the http query, then try to parse it
    if isinstance(post_time, str):
        try:
            post_time = date_parse(post_time)
        except:
            post_time = None

    # Get lecture notes
    lecture_notes: LectureNotes = LectureNotes.query.filter(
        LectureNotes.id == lecture_notes_id,
        LectureNotes.course_id == course_context.id,
    ).first()

    # If post time is None for whatever reason, then
    # default to what it is set as already
    if post_time is None:
        post_time = lecture_notes.post_time

    # Assert that the static file is within the current course context
    assert_course_context(lecture_notes)

    # Pull file from request (if there is one)
    stream, filename = get_request_file_stream(with_filename=True, fail_ok=True)

    # Update fields
    lecture_notes.post_time = post_time
    lecture_notes.title = title
    lecture_notes.description = description

    if stream is not None:
        lecture_notes.static_file.blob = stream
        lecture_notes.static_file.filename = filename
        lecture_notes.static_file.content_type = get_mime_type(stream)

    db.session.commit()

    return success_response(
        {
            "status": "Lecture notes update",
        }
    )


@lectures_.post("/upload")
@require_admin(unless_debug=True)
@json_response
def admin_lecture_upload():
    """
    Upload a new public static file. The file will immediately be
    publicly available.

    The StaticFiles are unique by the path specified by the admin. If the path
    already exists, then the file is replaced.

    params = {
      number: 0,
      title: 'this is the title',
      description: 'this is the description',
    }

    :return:
    """

    # Get fields from params
    post_time = request.args.get("post_time", default=None)
    title = request.args.get("title", default="")
    description = request.args.get("description", default="")

    # If post time was in the http query, then try to parse it
    if isinstance(post_time, str):
        try:
            post_time = date_parse(post_time)
        except:
            post_time = None

    # If post time is None for whatever reason, then
    # default to now
    if post_time is None:
        post_time = datetime.now()

    # Process the file upload
    blob = process_file_upload()

    # Create the lecture notes to match
    lecture_notes = LectureNotes(
        static_file_id=blob.id,
        course_id=course_context.id,
        post_time=post_time,
        title=title,
        description=description,
        hidden=False,
    )
    db.session.add(lecture_notes)
    db.session.commit()

    # Pass back the status
    return success_response(
        {
            "status": f"{blob.filename} uploaded",
            "blob": blob.data,
        }
    )
