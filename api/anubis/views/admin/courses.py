from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, Course, TAForCourse, ProfessorForCourse, User
from anubis.utils.data import row2dict
from anubis.utils.http.decorators import json_response, json_endpoint
from anubis.utils.http.https import success_response, error_response
from anubis.utils.lms.course import assert_course_superuser, get_course_context
from anubis.utils.auth import require_admin, require_superuser, current_user

courses_ = Blueprint("admin-courses", __name__, url_prefix="/admin/courses")


@courses_.route("/")
@courses_.route("/list")
@require_admin()
@json_response
def admin_courses_list():
    course = get_course_context()

    return success_response({
        "course": {"join_code": course.id[:6], **row2dict(course)},
    })


@courses_.route("/new")
@require_superuser()
@json_response
def admin_courses_new():
    course = Course(
        name="placeholder",
        course_code="placeholder",
        section="a",
        professor="placeholder",
    )
    db.session.add(course)
    db.session.commit()

    return success_response({
        "course": course.data,
        "status": "Created new course",
    })


@courses_.route("/save", methods=["POST"])
@require_admin()
@json_endpoint(required_fields=[("course", dict)])
def admin_courses_save_id(course: dict):
    course_id = course.get("id", None)
    db_course = Course.query.filter(Course.id == course_id).first()

    if db_course is None:
        return error_response("Course not found.")

    assert_course_superuser(course_id)

    for column in Course.__table__.columns:
        if column.name in course:
            setattr(db_course, column.name, course[column.name])

    try:
        db.session.commit()
    except (IntegrityError, DataError) as e:
        db.session.rollback()
        return error_response("Unable to save " + str(e))

    return success_response({"course": db_course.data, "status": "Changes saved."})


@courses_.route('/list/tas')
@require_admin()
@json_response
def admin_course_list_tas():
    course = get_course_context()

    tas = User.query.join(TAForCourse).filter(
        TAForCourse.course_id == course.id,
    ).all()

    return success_response({
        'users': [
            {
                'id': user.id,
                'netid': user.netid,
                'name': user.name,
                'github_username': user.github_username,
            }
            for user in tas
        ]
    })


@courses_.route('/list/professors')
@require_admin()
@json_response
def admin_course_list_professors():
    course = get_course_context()

    tas = User.query.join(ProfessorForCourse).filter(
        ProfessorForCourse.course_id == course.id,
    ).all()

    return success_response({
        'users': [
            {
                'id': user.id,
                'netid': user.netid,
                'name': user.name,
                'github_username': user.github_username,
            }
            for user in tas
        ]
    })


@courses_.route('/make/ta/<string:user_id>')
@require_admin()
@json_response
def admin_course_make_ta_id(user_id: str):
    course = get_course_context()

    other = User.query.filter(User.id == user_id).first()
    if other is None:
        return error_response('User id does not exist'), 400

    ta = TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
    ).first()
    if ta is not None:
        return error_response('They are already a TA'), 400

    ta = TAForCourse(
        owner_id=user_id,
        course_id=course.id,
    )
    db.session.add(ta)
    db.session.commit()

    return success_response({
        'status': 'TA added to course'
    })


@courses_.route('/remove/ta/<string:user_id>')
@require_admin()
@json_response
def admin_course_remove_ta_id(user_id: str):
    user = current_user()
    course = get_course_context()
    assert_course_superuser(course.id)

    other = User.query.filter(User.id == user_id).first()
    if other is None:
        return error_response('User id does not exist'), 400

    if other.id == user.id:
        return error_response('cannot remove yourself'), 400

    TAForCourse.query.filter(
        TAForCourse.owner_id == user_id,
        TAForCourse.course_id == course.id,
    ).delete()
    db.session.commit()

    return success_response({
        'status': 'TA removed from course',
        'variant': 'warning',
    })


@courses_.route('/make/professor/<string:user_id>')
@require_superuser()
@json_response
def admin_course_make_professor_id(user_id: str):
    course = get_course_context()

    other = User.query.filter(User.id == user_id).first()
    if other is None:
        return error_response('User id does not exist'), 400

    prof = ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
    ).first()
    if prof is not None:
        return error_response('They are already a TA'), 400

    prof = ProfessorForCourse(
        owner_id=user_id,
        course_id=course.id,
    )
    db.session.add(prof)
    db.session.commit()

    return success_response({
        'status': 'Professor added to course'
    })


@courses_.route('/remove/professor/<string:user_id>')
@require_superuser()
@json_response
def admin_course_remove_professor_id(user_id: str):
    user = current_user()
    course = get_course_context()

    other = User.query.filter(User.id == user_id).first()
    if other is None:
        return error_response('User id does not exist'), 400

    if other.id == user.id:
        return error_response('cannot remove yourself'), 400

    ProfessorForCourse.query.filter(
        ProfessorForCourse.owner_id == user_id,
        ProfessorForCourse.course_id == course.id,
    ).delete()
    db.session.commit()

    return success_response({
        'status': 'TA removed from course',
        'variant': 'warning',
    })
