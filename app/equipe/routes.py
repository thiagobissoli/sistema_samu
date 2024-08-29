from flask import render_template, redirect, url_for, request, jsonify, flash, send_file
from flask_login import login_required, current_user
from . import bp as equipe
from .forms import EquipeForm
from ..models import ControlePark, Previsao, Viatura, AlertaViatura, Equipe
from .. import db
from datetime import datetime
import pytz
import pandas as pd
import io
from app.auth.decorators import role_required

brasilia_tz = pytz.timezone('America/Sao_Paulo')

def current_time_brasilia():
    return datetime.now(brasilia_tz)


@equipe.route('/equipes', methods=['GET', 'POST'])
@login_required
def list_equipes():
    equipes = Equipe.query.all()
    return render_template('patio/list_equipes.html', equipes=equipes)

@equipe.route('/equipe/create', methods=['GET', 'POST'])
@login_required
def create_equipe():
    form = EquipeForm()
    if form.validate_on_submit():
        new_equipe = Equipe(equipe=form.equipe.data, tipo_suporte=form.tipo_suporte.data)
        db.session.add(new_equipe)
        db.session.commit()
        flash('Equipe criada com sucesso!', 'success')
        return redirect(url_for('patio.list_equipes'))
    return render_template('patio/create_equipe.html', form=form)

@equipe.route('/equipe/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_equipe(id):
    equipe = Equipe.query.get_or_404(id)
    form = EquipeForm(obj=equipe)
    if form.validate_on_submit():
        equipe.equipe = form.equipe.data
        equipe.tipo_suporte = form.tipo_suporte.data
        db.session.commit()
        flash('Equipe atualizada com sucesso!', 'success')
        return redirect(url_for('patio.list_equipes'))
    return render_template('patio/edit_equipe.html', form=form)

@equipe.route('/equipe/delete/<int:id>', methods=['POST'])
@login_required
def delete_equipe(id):
    equipe = Equipe.query.get_or_404(id)
    db.session.delete(equipe)
    db.session.commit()
    flash('Equipe excluída com sucesso!', 'success')
    return redirect(url_for('patio.list_equipes'))
