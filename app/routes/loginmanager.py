from app import login_manager
from app.services import loginmanager

@login_manager.user_loader
def load_user(user_id):
    return loginmanager.load_user(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return loginmanager.unauthorized()