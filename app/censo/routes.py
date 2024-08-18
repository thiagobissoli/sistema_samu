from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import Hospital, Censo, User
from .. import db
from . import bp as censo
from .forms import CensoForm
from ..utils import current_time_brasilia
from datetime import datetime
from app.auth.decorators import role_required

@censo.route('/registrar_censo', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Visitante')
def registrar_censo():
    form = CensoForm()
    if form.validate_on_submit():
        censo = Censo(
            hospital_id=current_user.hospital_id,
            leitos_ocupados=form.leitos_ocupados.data,
            observacao=form.observacao.data
        )
        db.session.add(censo)
        db.session.commit()
        flash('Censo registrado com sucesso.', 'success')
        return redirect(url_for('censo.registrar_censo'))
    return render_template('censo/registrar_censo.html', form=form)


@censo.route('/censo_mestre', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor' )
def censo_mestre():

    form = CensoForm()
    if form.validate_on_submit():
        hospital_id = request.form.get('hospital_id')
        censo = Censo(
            hospital_id=hospital_id,
            leitos_ocupados=form.leitos_ocupados.data,
            observacao=form.observacao.data
        )
        db.session.add(censo)
        db.session.commit()
        flash('Censo mestre registrado com sucesso.', 'success')
        return redirect(url_for('censo.censo_mestre'))

    hospitais = Hospital.query.all()
    return render_template('/censo/censo_mestre.html', form=form, hospitais=hospitais)


@censo.route('/')
@login_required
def index():
    censos = Censo.query.all()
    latest_censos = {}
    for censo in censos:
        if censo.hospital_id not in latest_censos or latest_censos[censo.hospital_id].data_hora < censo.data_hora:
            latest_censos[censo.hospital_id] = censo
    hospitals = Hospital.query.all()
    censo_data = []
    for hospital in hospitals:
        if hospital.id in latest_censos:
            censo = latest_censos[hospital.id]
            ocupacao = (censo.leitos_ocupados / hospital.leitos) * 100 if hospital.leitos > 0 else 0
            censo_data.append({
                'hospital': hospital.nome,
                'leitos_ocupados': censo.leitos_ocupados,
                'leitos_totais': hospital.leitos,
                'ocupacao': ocupacao,
                'observacao': censo.observacao,
                'data_hora': censo.data_hora
            })
        else:
            censo_data.append({
                'hospital': hospital.nome,
                'leitos_ocupados': 0,
                'leitos_totais': hospital.leitos,
                'ocupacao': 0,
                'observacao': 'Nenhum censo registrado.',
                'data_hora': None
            })

    return render_template('censo/index.html', censo_data=censo_data)


@censo.route('/censo_atualizado', methods=['GET'])
@login_required
def censo_atualizado():
    hospitais = Hospital.query.all()
    censos = Censo.query.order_by(Censo.data_hora.desc()).all()
    censo_dict = {}
    for censo in censos:
        if censo.hospital_id not in censo_dict:
            censo_dict[censo.hospital_id] = censo

    return render_template('censo/censo_atualizado.html', hospitais=hospitais, censo_dict=censo_dict)

