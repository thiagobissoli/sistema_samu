from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ViaturaForm(FlaskForm):
    vtr = StringField('VTR', validators=[DataRequired()])
    placa = StringField('Placa', validators=[DataRequired()])
    submit = SubmitField('Salvar')
