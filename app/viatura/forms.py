from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Equipe


class ViaturaForm(FlaskForm):
    vtr = StringField('VTR', validators=[DataRequired()])
    placa = StringField('Placa', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class ViaturaEquipeForm(FlaskForm):
    vtr = StringField('Nome ou Número da Viatura', validators=[DataRequired()])
    placa = StringField('Placa', validators=[DataRequired()])
    equipe = QuerySelectField('Equipe', query_factory=lambda: Equipe.query.all(), get_label='equipe', allow_blank=True)
    submit = SubmitField('Salvar')
