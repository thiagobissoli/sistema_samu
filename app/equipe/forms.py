from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, SelectField
from wtforms.validators import DataRequired


class EquipeForm(FlaskForm):
    equipe = StringField('Nome da Equipe', validators=[DataRequired()])
    tipo_suporte = SelectField('Tipo de Suporte',
                               choices=[('Básico', 'Básico'), ('Avançado', 'Avançado')],
                               validators=[DataRequired()])
    submit = SubmitField('Salvar')



