# /app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from sqlalchemy import inspect


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from .models import Role, User, Hospital  # Importa Role, User e Hospital dentro da função create_app

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .gestor import bp as gestor_bp
    app.register_blueprint(gestor_bp, url_prefix='/gestor')

    from .viatura import bp as viatura_bp
    app.register_blueprint(viatura_bp, url_prefix='/viatura')

    from .local import bp as local_bp
    app.register_blueprint(local_bp, url_prefix='/local')

    from .ncps import bp as ncps_bp
    app.register_blueprint(ncps_bp, url_prefix='/ncps')

    from .patio import bp as patio_bp
    app.register_blueprint(patio_bp, url_prefix='/patio')

    from .calendar import bp as calendar_bp
    app.register_blueprint(calendar_bp, url_prefix='/calendar')

    from app.censo import bp as censo_bp
    app.register_blueprint(censo_bp, url_prefix='/censo')

    from app.hospital import bp as hospital_bp
    app.register_blueprint(hospital_bp, url_prefix='/hospital')

    from app.workgroup import bp as workgroup_bp
    app.register_blueprint(workgroup_bp, url_prefix='/workgroup')

    from app.kanban import bp as kanban_bp
    app.register_blueprint(kanban_bp, url_prefix='/kanban')

    from app.migracao import bp as migracao_bp
    app.register_blueprint(migracao_bp, url_prefix='/migracao')

    with app.app_context():
        inspector = inspect(db.engine)
        # Verifica se as tabelas existem antes de criar roles e usuário admin
        if inspector.has_table('role') and inspector.has_table('user') and inspector.has_table('hospital'):
            ensure_default_hospital()
            ensure_roles_exist()
            ensure_admin_user()
    return app


def ensure_default_hospital():
    from .models import Hospital
    hospital = Hospital.query.first()
    if not hospital:
        hospital = Hospital(nome="Hospital Default", leitos=100)
        db.session.add(hospital)
        db.session.commit()


def ensure_roles_exist():
    from .models import Role
    roles = [
        'Usuario',
        'Visitante',
        'Supervisor',
        'Coordenador',
        'Assessor',
        'Qualidade',
        'Portaria',
        'Administrador'
    ]

    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
    db.session.commit()


def ensure_admin_user():
    from .models import Role, User, Hospital
    admin_role = Role.query.filter_by(name='Administrador').first()
    admin_user = User.query.filter_by(username='Administrador').first()

    if not admin_user:
        hospital = Hospital.query.first()
        if not hospital:
            hospital = Hospital(nome="Hospital Default", leitos=100)
            db.session.add(hospital)
            db.session.commit()

        admin_user = User(
            username='Administrador',
            email='admin@example.com',
            role=admin_role,
            is_active=True,
            hospital_id=hospital.id  # Atribui o ID do hospital existente
        )
        admin_user.set_password('Samu&$@192')
        db.session.add(admin_user)
        db.session.commit()

