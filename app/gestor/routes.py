from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as gestor
from .forms import GestorForm
from ..models import Gestor
from .. import db
from app.auth.decorators import role_required

@gestor.route('/gestores')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def list_gestores():
    gestores = Gestor.query.filter_by(deleted=False).all()
    return render_template('gestor/list_gestores.html', gestores=gestores)

@gestor.route('/gestor/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def create_gestor():
    form = GestorForm()
    if form.validate_on_submit():
        gestor = Gestor(nome=form.nome.data)
        db.session.add(gestor)
        db.session.commit()
        flash('Gestor criado com sucesso!', 'success')
        return redirect(url_for('gestor.list_gestores'))
    return render_template('gestor/create_gestor.html', form=form)

@gestor.route('/gestor/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def edit_gestor(id):
    gestor = Gestor.query.get_or_404(id)
    form = GestorForm(obj=gestor)
    if form.validate_on_submit():
        gestor.nome = form.nome.data
        db.session.commit()
        flash('Gestor atualizado com sucesso!', 'success')
        return redirect(url_for('gestor.list_gestores'))
    return render_template('gestor/edit_gestor.html', form=form, gestor=gestor)

@gestor.route('/gestor/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_gestor(id):
    gestor = Gestor.query.get_or_404(id)
    gestor.deleted = True
    db.session.commit()
    flash('Gestor marcado como excluído com sucesso!', 'success')
    return redirect(url_for('gestor.list_gestores'))
