from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

class GoogleFormsForm(FlaskForm):
    formulario = StringField('Formulário', validators=[DataRequired()])
    descricao = StringField('Descrição', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL(message='URL inválida')])
    roles = StringField('Perfis', validators=[DataRequired()])
    submit = SubmitField('Salvar')
