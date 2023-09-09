from anubis.models import User
from anubis.utils.config import get_config_str
from anubis.utils.logging import logger


def get_admin_user() -> User | None:
    admin_netid: str = get_config_str('ADMIN_NETID', None)
    if admin_netid is None:
        logger.warning(f'ADMIN_NETID not set')
        return

    # Get admin user
    user: User = User.query.filter(User.netid == admin_netid).first()
    if user is None:
        logger.warning(f'Admin user not found')
        return

    return user
