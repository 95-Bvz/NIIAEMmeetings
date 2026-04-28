import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import User
from app.decorators import admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Управление пользователями (панель администратора)"""
    all_users = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_role(user_id):
    """Изменение роли пользователя"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['admin', 'manager', 'user']:
        flash('Недопустимая роль.', 'danger')
        return redirect(url_for('admin.users'))
        
    if user.id == 1 and new_role != 'admin':
        flash('Нельзя изменить роль главного администратора!', 'danger')
        return redirect(url_for('admin.users'))
        
    user.role = new_role
    db.session.commit()
    logger.info(f'Роль пользователя {user.username} изменена на {new_role}')
    flash(f'Роль пользователя {user.username} успешно обновлена.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_status(user_id):
    """Блокировка или разблокировка пользователя"""
    user = User.query.get_or_404(user_id)
    
    if user.id == 1:
        flash('Нельзя заблокировать главного администратора!', 'danger')
        return redirect(url_for('admin.users'))
        
    # Инвертируем статус
    user.is_active = not getattr(user, 'is_active', True)
    db.session.commit()
    
    action = "разблокирован" if user.is_active else "заблокирован"
    logger.info(f'Пользователь {user.username} был {action}')
    flash(f'Аккаунт {user.username} {action}.', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Удаление пользователя"""
    user = User.query.get_or_404(user_id)
    
    if user.id == 1:
        flash('Нельзя удалить главного администратора!', 'danger')
        return redirect(url_for('admin.users'))
        
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    logger.warning(f'Пользователь {username} был удален администратором')
    flash(f'Пользователь {username} успешно удален.', 'info')
    return redirect(url_for('admin.users'))
