from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, SelectField
from wtforms.validators import DataRequired
from ..models import Viatura, Equipe
from wtforms_sqlalchemy.fields import QuerySelectField


def get_viaturas():
    return Viatura.query.all()

class ControleParkForm(FlaskForm):
    viatura = QuerySelectField('Viatura', query_factory=get_viaturas, get_label='vtr', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class PrevisaoForm(FlaskForm):
    viatura = QuerySelectField('Viatura', query_factory=get_viaturas, get_label='vtr', validators=[DataRequired()])
    hora_chegada = DateTimeField('Hora de Chegada', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Prever Chegada')


class AlertaViaturaForm(FlaskForm):
    viatura = QuerySelectField('Viatura', query_factory=get_viaturas, get_label='vtr', validators=[DataRequired()])
    descricao = SelectField('Descrição', choices=[
        ('Estoque mínimo atingido', 'Estoque mínimo atingido'),
        ('Combustível mínimo atingido', 'Combustível mínimo atingido'),
        ('Necessita Manutenção da VTR', 'Necessita Manutenção da VTR'),
        ('Necessita Troca de VTR', 'Necessita Troca de VTR'),
        ('Outros', 'Outros')
    ], validators=[DataRequired()])
    prioridade = SelectField('Prioridade', choices=[
        ('Alta', 'Alta'),
        ('Média', 'Média'),
        ('Baixa', 'Baixa')
    ], validators=[DataRequired()])
    submit = SubmitField('Registrar Alerta')


class EquipeForm(FlaskForm):
    equipe = StringField('Nome da Equipe', validators=[DataRequired()])
    tipo_suporte = SelectField('Tipo de Suporte',
                               choices=[('Básico', 'Básico'), ('Avançado', 'Avançado')],
                               validators=[DataRequired()])
    submit = SubmitField('Salvar')



