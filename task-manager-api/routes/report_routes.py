from flask import Blueprint
from controllers import report_ctrl

report_bp = Blueprint('reports', __name__)

report_bp.route('/reports/summary', methods=['GET'])(report_ctrl.summary_report)
report_bp.route('/reports/user/<int:user_id>', methods=['GET'])(report_ctrl.user_report)
report_bp.route('/categories', methods=['GET'])(report_ctrl.get_categories)
report_bp.route('/categories', methods=['POST'])(report_ctrl.create_category)
report_bp.route('/categories/<int:cat_id>', methods=['PUT'])(report_ctrl.update_category)
report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])(report_ctrl.delete_category)
