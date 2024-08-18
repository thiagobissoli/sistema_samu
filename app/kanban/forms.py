from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Email

class ProjectForm(FlaskForm):
    name = StringField('Nome do Projeto', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    submit = SubmitField('Salvar')

class ColumnForm(FlaskForm):
    name = StringField('Nome da Coluna', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    responsible_id = SelectField('Responsável', coerce=int)
    requester_id = SelectField('Solicitante', coerce=int)
    due_date = DateTimeLocalField('Prazo de Entrega', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    priority = SelectField('Prioridade', choices=[('Baixa', 'Baixa'), ('Média', 'Média'), ('Alta', 'Alta')])
    submit = SubmitField('Salvar')


class AddUserToProjectForm(FlaskForm):
    user_id = SelectField('Usuário', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Adicionar')