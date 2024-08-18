from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User, Role, Hospital


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar redefinição de senha')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    password2 = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Solicitar redefinição de senha')

class ResetPassForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    confirm_password = PasswordField('Confirme a Nova Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem corresponder.')])
    submit = SubmitField('Redefinir Senha')

def get_role_choices():
    return [(role.id, role.name) for role in Role.query.order_by('name').all()]


class RoleForm(FlaskForm):
    name = StringField('Perfil de Acesso', validators=[DataRequired()])
    submit = SubmitField('Salvar')

    def validate_name(self, name):
        role = Role.query.filter_by(name=name.data).first()
        if role is not None:
            raise ValidationError('Por favor, utlize um nome diferente para o perfil.')


class CreateUserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Perfil de Acesso', coerce=int, choices=[])
    hospital = SelectField('Hospital', coerce=int, choices=[], validators=[Optional()])
    is_active = BooleanField('É Ativo', default=True)
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.hospital.choices = [(0, '')] + [(hospital.id, hospital.nome) for hospital in Hospital.query.order_by(Hospital.nome).all()]

class EditUserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Perfil de Acesso', coerce=int, choices=[])
    hospital = SelectField('Hospital', coerce=int, choices=[], validators=[Optional()])
    is_active = BooleanField('É Ativo', default=True)
    submit = SubmitField('Salvar')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.hospital.choices = [(0, '')] + [(hospital.id, hospital.nome) for hospital in Hospital.query.order_by(Hospital.nome).all()]

class SelfUserForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Nova senha', validators=[EqualTo('password2', message='As senhas devem corresponder')])
    password2 = PasswordField('Repita a nova senha')
    submit = SubmitField('Salvar')

    def validate_email(self, email):
        if email.data != current_user.email and User.query.filter_by(email=email.data).first():
            raise ValidationError('Por favor, use um endereço de email diferente.')
