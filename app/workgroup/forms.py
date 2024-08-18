from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
from app.models import User

class WorkGroupForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class AddUserToWorkGroupForm(FlaskForm):
    users = SelectMultipleField('Usuários', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Adicionar Usuários')