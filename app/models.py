from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Table
from . import db

brasilia_tz = pytz.timezone('America/Sao_Paulo')

# Association table for many-to-many relationship between users and Kanban projects
project_user = Table('project_user', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('kanban_project.id'), primary_key=True)
)

def current_time_brasilia():
    return datetime.now(brasilia_tz)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True, info={'unique_index': 'uq_email'})
    password_hash = db.Column(db.String(512))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), default=True)
    workgroups = db.relationship('WorkGroup', secondary='workgroup_user', back_populates='users')
    projects = db.relationship('KanbanProject', secondary=project_user, back_populates='users')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    deleted = db.Column(db.Boolean, default=False)

    def set_password(self, senha):
        self.password_hash = generate_password_hash(senha)

    def check_password(self, senha):
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, senha)

    def get_id(self):
        return str(self.id)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    deleted = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

class Viatura(db.Model):
    __tablename__ = 'viatura'
    id = db.Column(db.Integer, primary_key=True)
    vtr = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(20), nullable=False)
    deleted = db.Column(db.Boolean, default=False)
    controles = db.relationship('ControlePark', backref='viatura', lazy=True)

class Gestor(db.Model):
    __tablename__ = 'gestor'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    deleted = db.Column(db.Boolean, default=False)

class Local(db.Model):
    __tablename__ = 'local'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    deleted = db.Column(db.Boolean, default=False)

class Ncps(db.Model):
    __tablename__ = 'ncps'
    id = db.Column(db.Integer, primary_key=True)
    data_hora_registro = db.Column(db.DateTime, nullable=False, default=current_time_brasilia)
    descricao = db.Column(db.Text, nullable=True)
    local = db.Column(db.String(100), nullable=True)
    local_padronizado_id = db.Column(db.Integer, ForeignKey('local.id'), nullable=True)
    local_padronizado = relationship('Local', backref='ncps')
    id_ocorrencia = db.Column(db.String(100), nullable=True)
    data_hora_ocorrencia = db.Column(db.DateTime)
    dano = db.Column(db.String(50))
    classificacao_incidente = db.Column(db.String(50))
    sugestao = db.Column(db.Text, nullable=True)
    procedente = db.Column(db.String(50))
    gestor_id = db.Column(db.Integer, ForeignKey('gestor.id'), nullable=True)
    gestor = relationship('Gestor', backref='ncps')
    coordenador_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)  # assumindo que você tem um modelo User
    coordenador = relationship('User', backref='ncps')
    macroprocesso = db.Column(db.String(50))
    seguranca = db.Column(db.String(50))
    sentinela = db.Column(db.String(50))
    impacto = db.Column(db.String(50))
    probabilidade = db.Column(db.String(50))
    controle = db.Column(db.String(50))
    causa = db.Column(db.String(50))
    plano = db.Column(db.Text, nullable=True)
    acao = db.Column(db.String(50))
    prazo = db.Column(db.DateTime)
    status = db.Column(db.String(50))
    deleted = db.Column(db.Boolean, default=False)

class ControlePark(db.Model):
    __tablename__ = 'ControlePark'
    id = db.Column(db.Integer, primary_key=True)
    viatura_id = db.Column(db.Integer, db.ForeignKey('viatura.id'), nullable=False)
    hora_entrada = db.Column(db.DateTime, nullable=False, default=current_time_brasilia)
    hora_saida = db.Column(db.DateTime, nullable=True)
    farmacia = db.Column(db.Integer, default=0)  # 0 = cinza, 1 = vermelho, 2 = verde
    limpeza = db.Column(db.Integer, default=0)  # 0 = cinza, 1 = vermelho, 2 = verde
    cme = db.Column(db.Integer, default=0)      # 0 = cinza, 1 = vermelho, 2 = verde
    frota = db.Column(db.Integer, default=0)    # 0 = cinza, 1 = vermelho, 2 = verde
    administrativo = db.Column(db.Integer, default=0)  # 0 = cinza, 1 = vermelho, 2 = verde


class Previsao(db.Model):
    __tablename__ = 'previsao'
    id = db.Column(db.Integer, primary_key=True)
    viatura_id = db.Column(db.Integer, db.ForeignKey('viatura.id'), nullable=False)
    hora_chegada = db.Column(db.DateTime, nullable=True)
    farmacia = db.Column(db.Integer, default=0)
    limpeza = db.Column(db.Integer, default=0)
    cme = db.Column(db.Integer, default=0)
    frota = db.Column(db.Integer, default=0)
    administrativo = db.Column(db.Integer, default=0)
    finalizacao = db.Column(db.Integer, default=0)  # 0 = não finalizado, 1 = confirmado entrada, 2 = cancelado previsão
    viatura = db.relationship('Viatura')


class Hospital(db.Model):
    __tablename__ = 'hospital'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    leitos = db.Column(db.Integer, nullable=False)
    censos = db.relationship('Censo', backref='hospital', lazy=True)
    users = db.relationship('User', backref='hospital', lazy=True)

class Censo(db.Model):
    __tablename__ = 'censo'
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=current_time_brasilia, nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    leitos_ocupados = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.Text, nullable=True)


class WorkGroup(db.Model):
    __tablename__ = 'workgroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    users = db.relationship('User', secondary='workgroup_user', back_populates='workgroups')

class WorkGroupUser(db.Model):
    __tablename__ = 'workgroup_user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'), primary_key=True)


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
    all_day = db.Column(db.Boolean, default=False)
    background_color = db.Column(db.String(20))
    border_color = db.Column(db.String(20))
    text_color = db.Column(db.String(20))
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'))

    def __repr__(self):
        return f'<CalendarEvent {self.title}>'


class KanbanProject(db.Model):
    __tablename__ = 'kanban_project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=current_time_brasilia, nullable=False)
    users = db.relationship('User', secondary=project_user, back_populates='projects')
    columns = db.relationship('KanbanColumn', backref='project', lazy=True, cascade="all, delete-orphan")

class KanbanColumn(db.Model):
    __tablename__ = 'kanban_column'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('kanban_project.id'), nullable=False)
    tasks = db.relationship('KanbanTask', backref='column', lazy=True, cascade="all, delete-orphan")

class KanbanTask(db.Model):
    __tablename__ = 'kanban_task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    responsible_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    responsible = db.relationship('User', foreign_keys=[responsible_id])
    requester = db.relationship('User', foreign_keys=[requester_id])
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(50))
    column_id = db.Column(db.Integer, db.ForeignKey('kanban_column.id'), nullable=False)

