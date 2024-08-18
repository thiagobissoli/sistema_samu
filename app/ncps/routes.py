from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from . import bp as ncps
from .forms import NcpsForm, SearchForm, NcpsReportForm
from ..models import Ncps
from .. import db
from datetime import datetime
import pytz
import pandas as pd
import csv
import os
from io import BytesIO
import xlsxwriter
from app.auth.decorators import role_required


brasilia_tz = pytz.timezone('America/Sao_Paulo')

@ncps.route('/create_ncps', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade', 'Supervisor', 'Assessor', 'Portaria')
def create_ncps():
    form = NcpsForm()
    form.data_hora_registro.data = datetime.now(brasilia_tz)
    if form.validate_on_submit():
        ncps = Ncps(
            data_hora_registro=form.data_hora_registro.data,
            descricao=form.descricao.data,
            local=form.local.data,
            id_ocorrencia=form.id_ocorrencia.data,
            data_hora_ocorrencia=form.data_hora_ocorrencia.data,
            sugestao=form.sugestao.data,
            status="0"
        )
        try:
            db.session.add(ncps)
            db.session.commit()
            flash(f'NCPS ID número {ncps.id} adicionado com sucesso! Anote o número do ID para acompanhar o processo.', 'success')
            return redirect(url_for('ncps.create_ncps'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao adicionar Ncps: {e}", 'danger')
    else:
        flash("Erros de validação", 'danger')
    return render_template('ncps/create_ncps.html', form=form)


@ncps.route('/edit_ncps/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Qualidade' )
def edit_ncps(id):
    ncps = Ncps.query.get(id)
    form = NcpsForm(obj=ncps)
    print(request.form)
    if form.validate_on_submit():
        ncps.descricao = form.descricao.data
        ncps.local = form.local.data
        ncps.local_padronizado = form.local_padronizado.data
        ncps.id_ocorrencia = form.id_ocorrencia.data
        ncps.data_hora_ocorrencia = form.data_hora_ocorrencia.data
        ncps.dano = form.dano.data
        ncps.classificacao_incidente = form.classificacao_incidente.data
        ncps.sugestao = form.sugestao.data
        ncps.procedente = form.procedente.data
        ncps.gestor = form.gestor.data
        ncps.coordenador = form.coordenador.data
        ncps.macroprocesso = form.macroprocesso.data
        ncps.seguranca = form.seguranca.data
        ncps.sentinela = form.sentinela.data
        ncps.impacto = form.impacto.data
        ncps.probabilidade = form.probabilidade.data
        ncps.controle = form.controle.data
        ncps.causa = form.causa.data
        ncps.plano = form.plano.data
        ncps.acao = form.acao.data
        ncps.prazo = form.prazo.data
        ncps.status = form.status.data
        db.session.commit()
        return redirect(url_for('ncps.list_ncps'))
    return render_template('ncps/edit_ncps.html', form=form)


@ncps.route('/edit_gestor_ncps/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def edit_gestor_ncps(id):
    ncps = Ncps.query.get(id)
    form = NcpsForm(obj=ncps)
    print(request.form)
    if form.validate_on_submit():
        ncps.descricao = form.descricao.data
        ncps.local = form.local.data
        ncps.local_padronizado = form.local_padronizado.data
        ncps.id_ocorrencia = form.id_ocorrencia.data
        ncps.data_hora_ocorrencia = form.data_hora_ocorrencia.data
        ncps.dano = form.dano.data
        ncps.classificacao_incidente = form.classificacao_incidente.data
        ncps.sugestao = form.sugestao.data
        ncps.procedente = form.procedente.data
        ncps.gestor = form.gestor.data
        ncps.coordenador = form.coordenador.data
        ncps.macroprocesso = form.macroprocesso.data
        ncps.seguranca = form.seguranca.data
        ncps.sentinela = form.sentinela.data
        ncps.impacto = form.impacto.data
        ncps.probabilidade = form.probabilidade.data
        ncps.controle = form.controle.data
        ncps.causa = form.causa.data
        ncps.plano = form.plano.data
        ncps.acao = form.acao.data
        ncps.prazo = form.prazo.data
        ncps.status = form.status.data
        db.session.commit()
        return redirect(url_for('ncps.list_gestor_ncps'))
    return render_template('ncps/edit_gestor_ncps.html', form=form)


@ncps.route('/ncps/delete/<int:id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def delete_ncps(id):
    ncps = Ncps.query.get_or_404(id)
    ncps.deleted = True
    db.session.commit()
    flash('NCPS marcada como excluído com sucesso!', 'success')
    return redirect(url_for('ncps.list_ncps'))


@ncps.route('/search_ncps', methods=['GET', 'POST'])
def search_ncps():
    form = SearchForm()
    if form.validate_on_submit():
        ncp = Ncps.query.get(form.id.data)
        if ncp:
            return redirect(url_for('ncps.detail_ncps', id=ncp.id))
    return render_template('ncps/search_ncps.html', form=form)


@ncps.route('/list_ncps', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def list_ncps():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    def parse_date(date_str):
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        return None

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    query = Ncps.query.filter_by(deleted=False)

    if start_date:
        query = query.filter(Ncps.data_hora_registro >= start_date)
    if end_date:
        query = query.filter(Ncps.data_hora_registro <= end_date)

    ncps_list = query.all()

    return render_template('ncps/list_ncps.html', ncps=ncps_list, start_date=start_date_str, end_date=end_date_str)


@ncps.route('/list_gestor_ncps', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def list_gestor_ncps():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    def parse_date(date_str):
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        return None

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    query = Ncps.query.filter_by(coordenador_id=current_user.id, status="1",deleted=False)

    if start_date:
        query = query.filter(Ncps.data_hora_registro >= start_date)
    if end_date:
        query = query.filter(Ncps.data_hora_registro <= end_date)

    ncps_list = query.all()

    return render_template('ncps/list_gestor_ncps.html', ncps=ncps_list, start_date=start_date_str, end_date=end_date_str)


@ncps.route('/list_hist_gestor_ncps', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def list_hist_gestor_ncps():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    def parse_date(date_str):
        for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        return None

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    query = Ncps.query.filter_by(coordenador_id=current_user.id,deleted=False)

    if start_date:
        query = query.filter(Ncps.data_hora_registro >= start_date)
    if end_date:
        query = query.filter(Ncps.data_hora_registro <= end_date)

    ncps_list = query.all()

    return render_template('ncps/list_gestor_ncps.html', ncps=ncps_list, start_date=start_date_str, end_date=end_date_str)


@ncps.route('/export_ncps_excel')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def export_ncps_excel():
    ncps_list = Ncps.query.all()
    data = []
    for ncp in ncps_list:
        data.append({
            'ID': ncp.id,
            'Data e Hora do Registro': ncp.data_hora_registro,
            'Descrição': ncp.descricao,
            'Local': ncp.local,
            'Local Padronizado': ncp.local_padronizado.nome if ncp.local_padronizado else None,
            'ID da Ocorrência': ncp.id_ocorrencia,
            'Data e Hora da Ocorrência': ncp.data_hora_ocorrencia,
            'Dano': ncp.dano,
            'Classificação do Incidente': ncp.classificacao_incidente,
            'Sugestão': ncp.sugestao,
            'Procedente': ncp.procedente,
            'Gestor': ncp.gestor.nome if ncp.gestor else None,
            'Coordenador': ncp.coordenador.name if ncp.coordenador else None,
            'Macroprocesso': ncp.macroprocesso,
            'Segurança do Paciente': ncp.seguranca,
            'Evento Sentinela': ncp.sentinela,
            'Impacto': ncp.impacto,
            'Probabilidade': ncp.probabilidade,
            'Controle': ncp.controle,
            'Causa Raiz': ncp.causa,
            'Plano de Ação': ncp.plano,
            'Ação': ncp.acao,
            'Prazo': ncp.prazo,
            'Status': ncp.status
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='NCPS')
        writer.close()
    output.seek(0)

    return send_file(output, download_name='ncps.xlsx', as_attachment=True)


@ncps.route('/detail/<int:id>')
def detail_ncps(id):
    ncp = Ncps.query.get_or_404(id)
    return render_template('ncps/detail_ncps.html', ncp=ncp)


@ncps.route('/ncpsPowerBIS@mu192&$')
def ncpsPowerBI():
    ncps_list = Ncps.query.filter_by(deleted=False).all()
    return render_template('ncps/ncpspowerbi.html', ncps=ncps_list)


@ncps.route('/ncps', methods=['GET', 'POST'])
def add_ncps():
    form = NcpsForm()
    form.data_hora_registro.data = datetime.now(brasilia_tz)
    if form.validate_on_submit():
        ncps = Ncps(
            data_hora_registro=form.data_hora_registro.data,
            descricao=form.descricao.data,
            local=form.local.data,
            id_ocorrencia=form.id_ocorrencia.data,
            data_hora_ocorrencia=form.data_hora_ocorrencia.data,
            sugestao=form.sugestao.data,
            status="0"
        )
        try:
            db.session.add(ncps)
            db.session.commit()
            flash(f'NCPS ID número {ncps.id} adicionado com sucesso! Anote o número do ID para acompanhar o processo.', 'success')
            return redirect(url_for('ncps.add_ncps'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao adicionar Ncps: {e}", 'danger')
    #else:
    #    flash("Erros de validação", 'danger')
    return render_template('ncps/add_ncps.html', form=form)


@ncps.route('/report_ncps', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade' )
def report_ncps():
    form = NcpsReportForm()
    ncps_list = []

    if form.validate_on_submit():
        gestor_id = form.gestor.data
        start_date = form.start_date.data
        end_date = form.end_date.data

        query = Ncps.query.filter_by(deleted=False)

        if gestor_id:
            query = query.filter_by(gestor_id=gestor_id)

        if start_date:
            query = query.filter(Ncps.data_hora_registro >= start_date)

        if end_date:
            query = query.filter(Ncps.data_hora_registro <= end_date)

        ncps_list = query.all()

    return render_template('ncps/report_ncps.html', form=form, ncps_list=ncps_list)


@ncps.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    form = SearchForm()
    if form.validate_on_submit():
        ncp = Ncps.query.get(form.id.data)
        if ncp:
            return redirect(url_for('ncps.detalhe_ncps', id=ncp.id))
    return render_template('ncps/pesquisa.html', form=form)


@ncps.route('/detalhe/<int:id>')
def detalhe_ncps(id):
    ncp = Ncps.query.get_or_404(id)
    return render_template('ncps/detalhe_ncps.html', ncp=ncp)
