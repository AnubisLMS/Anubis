import dateutil.parser
from flask import Blueprint

from anubis.lms.courses import assert_course_context, course_context
from anubis.models import ReservedIDETime, db, Assignment
from anubis.utils.auth.http import require_admin
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_endpoint, json_response, load_from_id

reserve_ = Blueprint("admin-reserve", __name__, url_prefix="/admin/reserve")


def get_course_reservations():
    reservations = ReservedIDETime.query.filter(
        ReservedIDETime.course_id == course_context.id,
    ).all()
    return [
        reservation.data
        for reservation in reservations
    ]


@reserve_.get('/list')
@require_admin()
@json_response
def admin_reserve_list():
    return success_response({'reservations': get_course_reservations()})


@reserve_.post('/add/<string:id>')
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_reserve_add(assignment: Assignment):
    assert_course_context(assignment)

    reserve = ReservedIDETime(
        assignment_id=assignment.id,
        course_id=assignment.course.id,
    )
    db.session.add(reserve)
    db.session.commit()

    return success_response({
        'status':       'Added reservation',
        'reservations': get_course_reservations(),
    })


@reserve_.delete('/delete/<string:id>')
@require_admin()
@load_from_id(ReservedIDETime, verify_owner=False)
def admin_reserve_del(reserve: ReservedIDETime):
    assert_course_context(reserve)

    db.session.delete(reserve)
    db.session.commit()
    return success_response({
        'status':       'Deleted reservation',
        'variant':      'warning',
        'reservations': get_course_reservations(),
    })


@reserve_.post("/save/<string:id>")
@require_admin()
@load_from_id(ReservedIDETime, verify_owner=False)
@json_endpoint(required_fields=[("reservation", dict)])
def admin_reserve_save(reserve: ReservedIDETime, reservation: dict):
    assert_course_context(reserve)

    reserve.start = dateutil.parser.parse(reservation.get('start'))
    reserve.end = dateutil.parser.parse(reservation.get('end'))
    db.session.add(reserve)
    db.session.commit()

    return success_response({
        'status':       'Saved',
        'reservations': get_course_reservations(),
    })
