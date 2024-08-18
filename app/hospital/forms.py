from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Hospital

class HospitalForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=1, max=100)])
    leitos = IntegerField('Leitos', validators=[DataRequired()])
    submit = SubmitField('Salvar')
