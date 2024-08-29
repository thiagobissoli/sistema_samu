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

class PrevisaoForm_bkp(FlaskForm):
    viatura = QuerySelectField('Viatura', query_factory=get_viaturas, get_label='vtr', validators=[DataRequired()])
    hora_chegada = DateTimeField('Hora de Chegada', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Prever Chegada')

class PrevisaoForm(FlaskForm):
    equipe = SelectField('Equipe', coerce=int, validators=[DataRequired()])
    hora_chegada = DateTimeField('Hora de Chegada', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(PrevisaoForm, self).__init__(*args, **kwargs)
        # Filtra as equipes que têm viaturas associadas
        self.equipe.choices = [(equipe.id, equipe.equipe) for equipe in
                               Equipe.query.filter(Equipe.viaturas.any()).all()]

class AlertaViaturaForm(FlaskForm):
    equipe = SelectField('Equipe', coerce=int, validators=[DataRequired()])  # Campo para selecionar a equipe
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


    def __init__(self, *args, **kwargs):
        super(AlertaViaturaForm, self).__init__(*args, **kwargs)
        self.equipe.choices = [(equipe.id, equipe.equipe) for equipe in Equipe.query.filter(Equipe.viaturas.any()).all()]


class EquipeForm(FlaskForm):
    equipe = StringField('Nome da Equipe', validators=[DataRequired()])
    tipo_suporte = SelectField('Tipo de Suporte',
                               choices=[('Básico', 'Básico'), ('Avançado', 'Avançado')],
                               validators=[DataRequired()])
    submit = SubmitField('Salvar')



