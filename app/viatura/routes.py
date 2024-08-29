from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as viatura
from .forms import ViaturaForm, ViaturaEquipeForm
from ..models import Viatura, HistoricoViaturaEquipe
from .. import db
from datetime import datetime
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


@viatura.route('/edit_equipe_viatura/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade', 'Supervisor')
def edit_equipe_viatura(id):
    viatura = Viatura.query.get_or_404(id)
    form = ViaturaEquipeForm(obj=viatura)

    if form.validate_on_submit():
        equipe_id = form.equipe.data.id if form.equipe.data else None

        # Verificar se a equipe já está associada a outra viatura
        if equipe_id:
            existing_viatura = Viatura.query.filter_by(equipe_id=equipe_id).first()
            if existing_viatura and existing_viatura.id != id:
                flash('Essa equipe já está associada a outra viatura!', 'error')
                return render_template('viatura/edit_equipe_viatura.html', form=form)

        # Atualizar o histórico se a equipe for trocada
        if viatura.equipe_id != equipe_id:
            # Fechar o período da equipe atual, se existir
            historico_atual = HistoricoViaturaEquipe.query.filter_by(viatura_id=viatura.id, data_fim=None).first()
            if historico_atual:
                historico_atual.data_fim = datetime.utcnow()
                db.session.add(historico_atual)

            # Iniciar um novo histórico se uma nova equipe for atribuída
            if equipe_id:
                novo_historico = HistoricoViaturaEquipe(
                    viatura_id=viatura.id,
                    equipe_id=equipe_id,
                    data_inicio=datetime.utcnow()
                )
                db.session.add(novo_historico)

        # Atualizar os dados da viatura
        viatura.vtr = form.vtr.data
        viatura.placa = form.placa.data
        viatura.equipe_id = equipe_id
        db.session.commit()
        flash('Viatura atualizada com sucesso!', 'success')
        return redirect(url_for('viatura.list_viaturas'))

    return render_template('viatura/edit_equipe_viatura.html', form=form)


@viatura.route('/delete_viatura/<int:id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_viatura(id):
    viatura = Viatura.query.get_or_404(id)
    viatura.deleted = True
    db.session.commit()
    flash('Viatura excluída com sucesso.', 'success')
    return redirect(url_for('viatura.list_viaturas'))


@viatura.route('/historico', methods=['GET'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade', 'Supervisor')
def historico_viaturas():
    historico = HistoricoViaturaEquipe.query.order_by(HistoricoViaturaEquipe.data_inicio.desc()).all()
    return render_template('viatura/historico_viaturas.html', historico=historico)
