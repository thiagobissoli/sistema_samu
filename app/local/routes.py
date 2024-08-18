from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as local
from .forms import LocalForm
from ..models import Local
from .. import db
from app.auth.decorators import role_required

@local.route('/list_locais')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def list_locais():
    locais = Local.query.filter_by(deleted=False).all()
    return render_template('local/list_locais.html', locais=locais)

@local.route('/create_local', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def create_local():
    form = LocalForm()
    if form.validate_on_submit():
        local = Local(nome=form.nome.data)
        db.session.add(local)
        db.session.commit()
        flash('Local criado com sucesso!', 'success')
        return redirect(url_for('local.list_locais'))
    return render_template('local/create_local.html', form=form)

@local.route('/edit_local/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def edit_local(id):
    local = Local.query.get_or_404(id)
    form = LocalForm(obj=local)
    if form.validate_on_submit():
        local.nome = form.nome.data
        db.session.commit()
        flash('Local atualizado com sucesso!', 'success')
        return redirect(url_for('local.list_locais'))
    return render_template('local/edit_local.html', form=form)

@local.route('/delete_local/<int:id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_local(id):
    local = Local.query.get_or_404(id)
    local.deleted = True
    db.session.commit()
    flash('Local excluído com sucesso.', 'success')
    return redirect(url_for('local.list_locais'))
