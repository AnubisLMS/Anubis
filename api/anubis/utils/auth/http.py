from functools import wraps

from anubis.models import ProfessorForCourse, TAForCourse
from anubis.utils.auth.user import get_current_user
from anubis.utils.data import is_debug
from anubis.utils.exceptions import AssertError, AuthenticationError


def require_user(unless_debug=False):
    """
    Wrap a function to require a user to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is an admin.
            if user is None:
                raise AuthenticationError()

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin(unless_debug=False):
    """
    Wrap a function to require an admin to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is an admin.
            if user is None:
                raise AuthenticationError("Request is anonymous")

            if user.is_superuser:
                return func(*args, **kwargs)

            ta = TAForCourse.query.filter(TAForCourse.owner_id == user.id).first()
            prof = ProfessorForCourse.query.filter(ProfessorForCourse.owner_id == user.id).first()

            if ta is None and prof is None:
                raise AuthenticationError("User is not ta or professor")

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_superuser(unless_debug=False):
    """
    Wrap a function to require an superuser to be logged in.
    If they are not logged in, they will get an Unathed
    error response with status code 401.

    :param unless_debug:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the user in the current
            # request context.
            user = get_current_user()

            # Bypass auth if the api is in debug
            # mode and unless_debug is true.
            if unless_debug and is_debug():
                return func(*args, **kwargs)

            # Check that there is a user specified
            # in the current request context, and
            # that use is a superuser.
            if user is None:
                raise AuthenticationError()

            # If the user is not a superuser, then return a 400 error
            # so it will be displayed in a snackbar.
            if user.is_superuser is False:
                raise AssertError("This requires superuser permissions", 200)

            # Pass the parameters to the
            # decorated function.
            return func(*args, **kwargs)

        return wrapper

    return decorator
