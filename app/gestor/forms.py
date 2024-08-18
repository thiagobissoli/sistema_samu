from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Gestor


class GestorForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    submit = SubmitField('Salvar')

def get_gestores():
    return Gestor.query.order_by(Gestor.nome).all()
