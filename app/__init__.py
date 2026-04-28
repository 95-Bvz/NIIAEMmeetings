import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    app.logger.setLevel(logging.INFO)
    app.logger.info('Приложение НИИ АЭМ запущено')

    from app.routes import main, auth, meetings, employees, rooms, reports, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(meetings.bp)
    app.register_blueprint(employees.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(admin.bp)

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template_string
        return render_template_string('''
            {% extends "base.html" %}
            {% block title %}Доступ запрещён{% endblock %}
            {% block content %}
            <div class="text-center py-5">
                <i class="bi bi-shield-x" style="font-size: 4rem; color: #dc3545;"></i>
                <h2 class="mt-3">Доступ запрещён</h2>
                <p class="text-muted">У вас недостаточно прав для выполнения этого действия.</p>
                <a href="{{ url_for('main.index') }}" class="btn btn-primary">На главную</a>
            </div>
            {% endblock %}
        '''), 403

    with app.app_context():
        db.create_all()
        # Миграция: добавляем недостающие колонки
        try:
            from sqlalchemy import text
            db.session.execute(text(
                'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE'
            ))
            db.session.commit()
            app.logger.info('Migration is_active: OK')
        except Exception as e:
            db.session.rollback()
            app.logger.info(f'Migration skipped: {e}')

    return app
