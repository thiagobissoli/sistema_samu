from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import Censo, Hospital

class CensoForm(FlaskForm):
    leitos_ocupados = IntegerField('Leitos Ocupados', validators=[DataRequired()])
    observacao = TextAreaField('Observação', validators=[Optional(), Length(max=30, message='Observação deve ter no máximo 30 caracteres.')])
    submit = SubmitField('Registrar Censo')


