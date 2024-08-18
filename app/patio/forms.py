from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
from ..models import Viatura
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



