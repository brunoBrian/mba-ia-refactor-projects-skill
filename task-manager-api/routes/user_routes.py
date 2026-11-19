from flask import Blueprint
from controllers import user_ctrl

user_bp = Blueprint('users', __name__)

user_bp.route('/users', methods=['GET'])(user_ctrl.get_users)
user_bp.route('/users/<int:user_id>', methods=['GET'])(user_ctrl.get_user)
user_bp.route('/users', methods=['POST'])(user_ctrl.create_user)
user_bp.route('/users/<int:user_id>', methods=['PUT'])(user_ctrl.update_user)
user_bp.route('/users/<int:user_id>', methods=['DELETE'])(user_ctrl.delete_user)
user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])(user_ctrl.get_user_tasks)
user_bp.route('/login', methods=['POST'])(user_ctrl.login)
