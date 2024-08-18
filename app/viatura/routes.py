from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as viatura
from .forms import ViaturaForm
from ..models import Viatura
from .. import db
from app.auth.decorators import role_required

@viatura.route('/list_viaturas')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def list_viaturas():
    viaturas = Viatura.query.filter_by(deleted=False).all()
    return render_template('viatura/list_viaturas.html', viaturas=viaturas)

@viatura.route('/create_viatura', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def create_viatura():
    form = ViaturaForm()
    if form.validate_on_submit():
        viatura = Viatura(vtr=form.vtr.data, placa=form.placa.data)
        db.session.add(viatura)
        db.session.commit()
        flash('Viatura criada com sucesso!', 'success')
        return redirect(url_for('viatura.list_viaturas'))
    return render_template('viatura/create_viatura.html', form=form)

@viatura.route('/edit_viatura/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def edit_viatura(id):
    viatura = Viatura.query.get_or_404(id)
    form = ViaturaForm(obj=viatura)
    if form.validate_on_submit():
        viatura.vtr = form.vtr.data
        viatura.placa = form.placa.data
        db.session.commit()
        flash('Viatura atualizada com sucesso!', 'success')
        return redirect(url_for('viatura.list_viaturas'))
    return render_template('viatura/edit_viatura.html', form=form)

@viatura.route('/delete_viatura/<int:id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_viatura(id):
    viatura = Viatura.query.get_or_404(id)
    viatura.deleted = True
    db.session.commit()
    flash('Viatura excluída com sucesso.', 'success')
    return redirect(url_for('viatura.list_viaturas'))
