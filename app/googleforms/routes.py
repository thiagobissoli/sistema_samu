from flask import render_template, redirect, url_for, request, jsonify, flash, send_file
from flask_login import login_required, current_user
from . import bp as googleforms
from .forms import GoogleFormsForm
from ..models import GoogleForms
from .. import db
from datetime import datetime
import pytz
import pandas as pd
import io
from app.auth.decorators import role_required

brasilia_tz = pytz.timezone('America/Sao_Paulo')

def current_time_brasilia():
    return datetime.now(brasilia_tz)

@googleforms.route('/google_forms', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade', 'Supervisor')
def list_google_forms():
    forms = GoogleForms.query.all()
    return render_template('googleforms/google_forms_list.html', forms=forms)

@googleforms.route('/google_forms/new', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador')
def new_google_form():
    form = GoogleFormsForm()
    if form.validate_on_submit():
        new_form = GoogleForms(
            formulario=form.formulario.data,
            descricao=form.descricao.data,
            url=form.url.data,
            roles=form.roles.data
        )
        db.session.add(new_form)
        db.session.commit()
        flash('Google Form criado com sucesso!', 'success')
        return redirect(url_for('googleforms.list_google_forms'))
    return render_template('googleforms/google_forms_form.html', form=form)

@googleforms.route('/google_forms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador')
def edit_google_form(id):
    google_form = GoogleForms.query.get_or_404(id)
    form = GoogleFormsForm(obj=google_form)
    if form.validate_on_submit():
        google_form.formulario = form.formulario.data
        google_form.descricao = form.descricao.data
        google_form.url = form.url.data
        google_form.roles = form.roles.data
        db.session.commit()
        flash('Google Form atualizado com sucesso!', 'success')
        return redirect(url_for('googleforms.list_google_forms'))
    return render_template('googleforms/google_forms_form.html', form=form)

@googleforms.route('/google_forms/delete/<int:id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador')
def delete_google_form(id):
    google_form = GoogleForms.query.get_or_404(id)
    db.session.delete(google_form)
    db.session.commit()
    flash('Google Form excluído com sucesso!', 'success')
    return redirect(url_for('googleforms.list_google_forms'))

@googleforms.route('/google_forms/view/<int:id>', methods=['GET'])
@login_required
def view_google_form(id):
    google_form = GoogleForms.query.get_or_404(id)
    return render_template('googleforms/view_google_form.html', google_form=google_form)
