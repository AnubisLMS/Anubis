from flask import Blueprint, request

from anubis.models import db, LectureNotes
from anubis.utils.data import req_assert
from anubis.utils.auth import require_admin
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.files import process_file_upload, get_mime_type
from anubis.utils.http.https import success_response, get_number_arg, get_request_file_stream
from anubis.utils.lms.courses import get_course_context, assert_course_context

lectures_ = Blueprint('admin-lectures', __name__, url_prefix='/admin/lectures')


@lectures_.get("/list")
@require_admin()
@json_response
def admin_static_lectures_list():
    """
    List all lecture notes for the course

    /admin/lecture/list

    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Build Query. Defer the blob field so
    # it is not loaded.
    query = LectureNotes.query \
        .filter(LectureNotes.course_id == course.id) \
        .order_by(LectureNotes.number.desc())

    # Get all public static files within this course
    lectures = query.all()

    # Pass back the list of files
    return success_response({
        "lectures": [lecture.data for lecture in lectures]
    })


@lectures_.get('/delete/<string:lecture_notes_id>')
@require_admin()
@json_response
def admin_lecture_delete_lecture_id(lecture_notes_id: str):
    """
    Delete a course lecture notes.

    :param lecture_notes_id:
    :return:
    """

    # Get course context
    course = get_course_context()

    # Get lecture notes
    lecture_notes = LectureNotes.query.filter(
        LectureNotes.id == lecture_notes_id,
        LectureNotes.course_id == course.id,
    ).first()

    # Assert that the static file is within the current course context
    assert_course_context(lecture_notes)

    # Make sure we got one
    req_assert(lecture_notes is not None, message='Lecture notes not found')

    # Mark the notes for deletion
    db.session.delete(lecture_notes)

    # Commit the delete
    db.session.commit()

    return success_response({
        'status': 'Lecture Notes deleted',
        'variant': 'warning',
    })


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

    # Get course context
    course = get_course_context()

    # Get fields from params
    number = get_number_arg('number', default_value=1, reject_negative=True)
    title = request.args.get('title', default='')
    description = request.args.get('description', default='')

    # Get lecture notes
    lecture_notes: LectureNotes = LectureNotes.query.filter(
        LectureNotes.id == lecture_notes_id,
        LectureNotes.course_id == course.id,
    ).first()

    # Assert that the static file is within the current course context
    assert_course_context(lecture_notes)

    # Pull file from request (if there is one)
    stream, filename = get_request_file_stream(with_filename=True, fail_ok=True)

    # Update fields
    lecture_notes.number = number
    lecture_notes.title = title
    lecture_notes.description = description

    if stream is not None:
        lecture_notes.static_file.blob = stream
        lecture_notes.static_file.filename = filename
        lecture_notes.static_file.content_type = get_mime_type(stream)

    db.session.commit()

    return success_response({
        'status': 'Lecture notes update',
    })


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

    # Get course context
    course = get_course_context()

    # Get fields from params
    number = get_number_arg('number', default_value=1, reject_negative=True)
    title = request.args.get('title', default='')
    description = request.args.get('description', default='')

    # Process the file upload
    blob = process_file_upload()

    # Create the lecture notes to match
    lecture_notes = LectureNotes(
        static_file_id=blob.id,
        course_id=course.id,
        number=number,
        title=title,
        description=description,
        hidden=False,
    )
    db.session.add(lecture_notes)
    db.session.commit()

    # Pass back the status
    return success_response({
        "status": f"{blob.filename} uploaded",
        "blob": blob.data,
    })
