from storage import users
from config import ROLE_MEMBER

def get_role(user_id):
    return users.get(user_id, ROLE_MEMBER)

def set_role(user_id, role):
    users[user_id] = role
