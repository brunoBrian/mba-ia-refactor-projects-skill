from flask import Blueprint
from controllers import task_ctrl

task_bp = Blueprint('tasks', __name__)

task_bp.route('/tasks', methods=['GET'])(task_ctrl.get_tasks)
task_bp.route('/tasks/search', methods=['GET'])(task_ctrl.search_tasks)
task_bp.route('/tasks/stats', methods=['GET'])(task_ctrl.task_stats)
task_bp.route('/tasks/<int:task_id>', methods=['GET'])(task_ctrl.get_task)
task_bp.route('/tasks', methods=['POST'])(task_ctrl.create_task)
task_bp.route('/tasks/<int:task_id>', methods=['PUT'])(task_ctrl.update_task)
task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])(task_ctrl.delete_task)
