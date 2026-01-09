from config import *

ROLE_PRIORITY = {
    ROLE_HOST: 4,
    ROLE_STAFF: 3,
    ROLE_DJ: 2,
    ROLE_MEMBER: 1
}

def has_access(user_role, required_role):
    return ROLE_PRIORITY.get(user_role, 0) >= ROLE_PRIORITY.get(required_role, 0)
