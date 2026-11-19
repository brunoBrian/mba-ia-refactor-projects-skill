from flask import jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timedelta


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priorities = {str(i): Task.query.filter_by(priority=i).count() for i in range(1, 6)}
    priority_labels = ['critical', 'high', 'medium', 'low', 'minimal']

    all_tasks = Task.query.all()
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (datetime.utcnow() - t.due_date).days
        }
        for t in all_tasks if t.is_overdue()
    ]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(Task.status == 'done', Task.updated_at >= seven_days_ago).count()

    users = User.query.all()
    user_stats = []
    for u in users:
        user_tasks = Task.query.filter_by(user_id=u.id).all()
        total = len(user_tasks)
        completed = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })

    return jsonify({
        'generated_at': str(datetime.utcnow()),
        'overview': {'total_tasks': total_tasks, 'total_users': total_users, 'total_categories': total_categories},
        'tasks_by_status': {'pending': pending, 'in_progress': in_progress, 'done': done, 'cancelled': cancelled},
        'tasks_by_priority': {label: int(priorities[str(i + 1)]) for i, label in enumerate(priority_labels)},
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {'tasks_created_last_7_days': recent_tasks, 'tasks_completed_last_7_days': recent_done},
        'user_productivity': user_stats,
    }), 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = sum(1 for t in tasks if t.status == 'done')
    pending = sum(1 for t in tasks if t.status == 'pending')
    in_progress = sum(1 for t in tasks if t.status == 'in_progress')
    cancelled = sum(1 for t in tasks if t.status == 'cancelled')
    overdue = sum(1 for t in tasks if t.is_overdue())
    high_priority = sum(1 for t in tasks if t.priority <= 2)

    return jsonify({
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done, 'pending': pending, 'in_progress': in_progress,
            'cancelled': cancelled, 'overdue': overdue, 'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
    }), 200


def get_categories():
    from models.category import Category
    categories = Category.query.all()
    result = []
    for c in categories:
        d = c.to_dict()
        d['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(d)
    return jsonify(result), 200


def create_category():
    from flask import request
    from models.category import Category
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'Nome é obrigatório'}), 400

    cat = Category()
    cat.name = data['name']
    cat.description = data.get('description', '')
    cat.color = data.get('color', '#000000')

    try:
        db.session.add(cat)
        db.session.commit()
        return jsonify(cat.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar categoria'}), 500


def update_category(cat_id):
    from flask import request
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json()
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500
