from flask import render_template, redirect, url_for, request, jsonify, flash, send_file
from flask_login import login_required, current_user
from . import bp as patio
from .forms import ControleParkForm, PrevisaoForm, AlertaViaturaForm, EquipeForm
from ..models import ControlePark, Previsao, Viatura, AlertaViatura, Equipe, HistoricoViaturaEquipe
from .. import db
from datetime import datetime
import pytz
import pandas as pd
import io
from app.auth.decorators import role_required

brasilia_tz = pytz.timezone('America/Sao_Paulo')

def current_time_brasilia():
    return datetime.now(brasilia_tz)


@patio.route('/supervisao', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def supervisao():
    controle_form = ControleParkForm()
    previsao_form = PrevisaoForm()

    if 'controle_submit' in request.form and controle_form.validate():
        viatura = controle_form.viatura.data
        equipe = viatura.equipe  # Busca a equipe associada à viatura automaticamente

        if not equipe:
            flash('Nenhuma equipe associada à viatura selecionada!', 'danger')
            return redirect(url_for('patio.supervisao'))

        # Cria o registro no ControlePark
        new_control = ControlePark(
            viatura=viatura,
            equipe=equipe,
            farmacia=0,
            limpeza=0,
            cme=0,
            frota=0,
            administrativo=0,
            hora_entrada=current_time_brasilia()
        )
        db.session.add(new_control)

        # Registra no histórico
        new_historico = HistoricoViaturaEquipe(
            viatura_id=new_control.viatura_id,
            equipe_id=new_control.equipe_id,
            data_inicio=new_control.hora_entrada
        )
        db.session.add(new_historico)
        db.session.commit()

        flash('Controle registrado com sucesso!', 'success')
        return redirect(url_for('patio.supervisao'))

    if 'previsao_submit' in request.form and previsao_form.validate():
        equipe_id = previsao_form.equipe.data
        # Recupere a viatura associada à equipe selecionada
        viatura = Viatura.query.filter_by(equipe_id=equipe_id).first()

        if not viatura:
            flash('Nenhuma viatura associada à equipe selecionada!', 'danger')
            return redirect(url_for('patio.supervisao'))

        new_previsao = Previsao(viatura_id=viatura.id, hora_chegada=previsao_form.hora_chegada.data)
        db.session.add(new_previsao)
        db.session.commit()
        flash('Previsão registrada com sucesso!', 'success')
        return redirect(url_for('patio.supervisao'))

    # Consultar previsões e viaturas estacionadas
    previsoes = Previsao.query.filter_by(finalizacao=0).all()
    parked_viaturas = ControlePark.query.filter_by(hora_saida=None).all()
    alertas = AlertaViatura.query.filter_by(status="Pendente").all()

    # Ajustar o timezone para viaturas estacionadas
    for record in parked_viaturas:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = brasilia_tz.localize(record.hora_entrada)

    return render_template('patio/supervisao.html',
                           controle_form=controle_form,
                           previsao_form=previsao_form,
                           previsoes=previsoes,
                           parked_viaturas=parked_viaturas,
                           alertas=alertas,  # Passar os alertas para o template
                           datetime=datetime,
                           current_time=current_time_brasilia()
                           )


@patio.route('/toggle-checkpoint', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor', 'Assessor')
def toggle_checkpoint():
    data = request.json
    record_id = data.get('record_id')
    checkpoint_name = data.get('checkpoint_name')

    record = ControlePark.query.get(record_id)

    if not record or not checkpoint_name:
        return jsonify(status="error", message="Invalid record ID or checkpoint name")

    try:
        current_value = getattr(record, checkpoint_name)
        if current_value == 0:
            new_value = 1
        elif current_value == 1:
            new_value = 2
        else:
            new_value = 0
        setattr(record, checkpoint_name, new_value)
        db.session.commit()
        return jsonify(status="success", new_value=new_value)
    except AttributeError:
        return jsonify(status="error", message=f"Invalid attribute name: {checkpoint_name}")

@patio.route('/toggle-previsao', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def toggle_previsao():
    data = request.json
    record_id = data.get('record_id')
    checkpoint_name = data.get('checkpoint_name')

    record = Previsao.query.get(record_id)

    if not record or not checkpoint_name:
        return jsonify(status="error", message="Invalid record ID or checkpoint name")

    try:
        current_value = getattr(record, checkpoint_name)
        if current_value == 0:
            new_value = 1
        else:
            new_value = 0
        setattr(record, checkpoint_name, new_value)
        db.session.commit()
        return jsonify(status="success", new_value=new_value)
    except AttributeError:
        return jsonify(status="error", message=f"Invalid attribute name: {checkpoint_name}")


@patio.route('/register_cancel/<int:control_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def register_cancel(control_id):
    previsao = Previsao.query.get(control_id)

    if not previsao:
        return redirect(url_for('patio.supervisao'))

    previsao.finalizacao = 2  # Define finalizacao como 2 (cancelado)
    db.session.commit()
    flash('Previsão cancelada com sucesso!', 'success')
    return redirect(url_for('patio.supervisao'))


@patio.route('/register_exit/<int:control_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor', 'Portaria')
def register_exit(control_id):
    local_time = datetime.now(brasilia_tz)

    control_record = ControlePark.query.get_or_404(control_id)
    control_record.hora_saida = local_time
    db.session.commit()
    flash('Saída registrada com sucesso!', 'success')
    return redirect(url_for('patio.portaria'))

@patio.route('/checkpoint', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor', 'Assessor')
def checkpoint():
    form = ControleParkForm()
    if form.validate_on_submit():
        new_control = ControlePark(viatura=form.viatura.data)
        db.session.add(new_control)
        db.session.commit()
        flash('Controle registrado com sucesso!', 'success')
        return redirect(url_for('patio.checkpoint'))

    previsoes = Previsao.query.filter_by(finalizacao=0).all()
    parked_viaturas = ControlePark.query.filter_by(hora_saida=None).all()

    for record in parked_viaturas:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = brasilia_tz.localize(record.hora_entrada)

    return render_template('patio/checkpoint.html',
                           form=form,
                           previsoes=previsoes,
                           parked_viaturas=parked_viaturas,
                           datetime=datetime,
                           current_time=current_time_brasilia()
                           )

@patio.route('/controlepark', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade', 'Supervisor', 'Assessor', 'Portaria')
def controlepark():
    controle_form = ControleParkForm()
    previsao_form = PrevisaoForm()

    if 'controle_submit' in request.form and controle_form.validate():
        new_control = ControlePark(viatura=controle_form.viatura.data)
        db.session.add(new_control)
        viatura_id = controle_form.viatura.data.id
        existing_previsao = Previsao.query.filter_by(viatura_id=viatura_id).first()
        if existing_previsao:
            db.session.delete(existing_previsao)
        db.session.commit()
        flash('Controle registrado com sucesso!', 'success')
        return redirect(url_for('patio.controlepark'))

    if 'previsao_submit' in request.form and previsao_form.validate():
        viatura_id = previsao_form.viatura.data.id
        new_previsao = Previsao(viatura_id=viatura_id, hora_chegada=previsao_form.hora_chegada.data)
        db.session.add(new_previsao)
        db.session.commit()
        flash('Previsão registrada com sucesso!', 'success')
        return redirect(url_for('patio.controlepark'))

    previsoes = Previsao.query.all()
    parked_viaturas = ControlePark.query.filter_by(hora_saida=None).all()

    for record in parked_viaturas:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = brasilia_tz.localize(record.hora_entrada)

    return render_template('patio/controlepark.html',
                           controle_form=controle_form,
                           previsao_form=previsao_form,
                           previsoes=previsoes,
                           parked_viaturas=parked_viaturas,
                           datetime=datetime,
                           current_time=current_time_brasilia()
                           )

@patio.route('/portaria', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor', 'Portaria')
def portaria():
    form = ControleParkForm()

    if form.validate_on_submit():
        viatura = form.viatura.data

        # Verifica se a viatura tem uma equipe associada
        if not viatura.equipe:
            flash('A viatura selecionada não possui uma equipe associada.', 'danger')
            return redirect(url_for('patio.portaria'))

        # Cria um novo controle para a viatura que está entrando
        new_control = ControlePark(
            viatura=viatura,
            equipe=viatura.equipe,  # Associa a equipe da viatura ao controle
            farmacia=0,
            limpeza=0,
            cme=0,
            frota=0,
            administrativo=0,
            hora_entrada=current_time_brasilia()
        )
        db.session.add(new_control)

        # Verifica se a viatura está na tabela de previsão
        existing_previsao = Previsao.query.filter_by(viatura_id=viatura.id, finalizacao=0).first()
        if existing_previsao:
            # Atualiza a previsão para finalizado
            existing_previsao.finalizacao = 1

            # Transfere os serviços previstos para a tabela ControlePark
            new_control.farmacia = existing_previsao.farmacia
            new_control.limpeza = existing_previsao.limpeza
            new_control.cme = existing_previsao.cme
            new_control.frota = existing_previsao.frota
            new_control.administrativo = existing_previsao.administrativo

            db.session.add(new_control)
            db.session.commit()
        else:
            db.session.commit()

        flash('Entrada registrada com sucesso!', 'success')
        return redirect(url_for('patio.portaria'))

    parked_viaturas = ControlePark.query.filter_by(hora_saida=None).all()

    for record in parked_viaturas:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = brasilia_tz.localize(record.hora_entrada)

    return render_template(
        'patio/portaria.html',
        form=form,
        parked_viaturas=parked_viaturas,
        datetime=datetime,
        current_time=current_time_brasilia()
    )



@patio.route('/relatorio')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def relatorio():
    controles = ControlePark.query.all()
    previsoes = Previsao.query.all()
    return render_template('patio/relatorio.html', controles=controles, previsoes=previsoes)


@patio.route('/exportar_relatorio')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def exportar_relatorio():
    controles = ControlePark.query.all()
    previsoes = Previsao.query.all()

    # Criar DataFrame para controles
    controle_data = [{
        'ID': controle.id,
        'Viatura': controle.viatura.vtr,
        'Placa': controle.viatura.placa,
        'Hora de Entrada': controle.hora_entrada,
        'Hora de Saída': controle.hora_saida if controle.hora_saida else 'N/A',
        'Farmácia': 'N/A' if controle.farmacia == 0 else 'Faltou' if controle.farmacia == 1 else 'Cumpriu',
        'Limpeza': 'N/A' if controle.limpeza == 0 else 'Faltou' if controle.limpeza == 1 else 'Cumpriu',
        'CME': 'N/A' if controle.cme == 0 else 'Faltou' if controle.cme == 1 else 'Cumpriu',
        'Frota': 'N/A' if controle.frota == 0 else 'Faltou' if controle.frota == 1 else 'Cumpriu',
        'Administrativo': 'N/A' if controle.administrativo == 0 else 'Faltou' if controle.administrativo == 1 else 'Cumpriu',
    } for controle in controles]

    df_controle = pd.DataFrame(controle_data)

    # Criar DataFrame para previsoes
    previsao_data = [{
        'ID': previsao.id,
        'Viatura': previsao.viatura.vtr,
        'Hora de Chegada': previsao.hora_chegada if previsao.hora_chegada else 'N/A',
        'Farmácia': 'N/A' if previsao.farmacia == 0 else 'Previsto',
        'Limpeza': 'N/A' if previsao.limpeza == 0 else 'Previsto',
        'CME': 'N/A' if previsao.cme == 0 else 'Previsto',
        'Frota': 'N/A' if previsao.frota == 0 else 'Previsto',
        'Administrativo': 'N/A' if previsao.administrativo == 0 else 'Previsto',
        'Finalização': 'N/A' if previsao.finalizacao == 0 else 'Confirmado entrada' if previsao.finalizacao == 1 else 'Cancelado previsão',
    } for previsao in previsoes]

    df_previsao = pd.DataFrame(previsao_data)

    # Escrever para um arquivo Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_controle.to_excel(writer, sheet_name='EntradaPatio', index=False)
        df_previsao.to_excel(writer, sheet_name='PrevisaoPatio', index=False)

    output.seek(0)

    return send_file(output, download_name="relatorio.xlsx", as_attachment=True)



@patio.route('/index')
@login_required
def index():
    current_time = current_time_brasilia()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Filtrando os controles que têm hora_saida no dia atual
    controles = ControlePark.query.filter(ControlePark.hora_saida.is_(None)).all()
    previsoes = Previsao.query.filter_by(finalizacao=0).all()

    # Filtrando todos os controles no dia atual para o gráfico
    controles_grafico = ControlePark.query.all()

    # Calculando as porcentagens para o gráfico
    farmacia_count = sum(1 for controle in controles_grafico if controle.farmacia == 2)
    limpeza_count = sum(1 for controle in controles_grafico if controle.limpeza == 2)
    cme_count = sum(1 for controle in controles_grafico if controle.cme == 2)
    frota_count = sum(1 for controle in controles_grafico if controle.frota == 2)
    administrativo_count = sum(1 for controle in controles_grafico if controle.administrativo == 2)
    total_count = len(controles_grafico)

    percentages = {
        "farmacia": (farmacia_count / total_count) * 100 if total_count > 0 else 0,
        "limpeza": (limpeza_count / total_count) * 100 if total_count > 0 else 0,
        "cme": (cme_count / total_count) * 100 if total_count > 0 else 0,
        "frota": (frota_count / total_count) * 100 if total_count > 0 else 0,
        "administrativo": (administrativo_count / total_count) * 100 if total_count > 0 else 0,
    }

    for record in controles:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = brasilia_tz.localize(record.hora_entrada)

    return render_template('main/ncps.html', controles=controles, previsoes=previsoes, percentages=percentages, current_time=current_time)


@patio.route('/alerta_viatura', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def alerta_viatura():
    alerta_form = AlertaViaturaForm()

    if alerta_form.validate_on_submit():
        equipe = Equipe.query.get(alerta_form.equipe.data)
        if not equipe:
            flash('Equipe inválida!', 'danger')
            return redirect(url_for('patio.alerta_viatura'))

        if not equipe.viaturas:
            flash('Nenhuma viatura está associada a esta equipe!', 'danger')
            return redirect(url_for('patio.alerta_viatura'))

        viatura = equipe.viaturas[0]  # Assume que cada equipe tem uma única viatura associada

        new_alerta = AlertaViatura(
            viatura_id=viatura.id,
            equipe_id=equipe.id,  # Definindo o equipe_id
            descricao=alerta_form.descricao.data,
            prioridade=alerta_form.prioridade.data,
            status="Pendente"  # Define o status como Pendente
        )
        db.session.add(new_alerta)
        db.session.commit()
        flash('Alerta de viatura criado com sucesso!', 'success')
        return redirect(url_for('patio.supervisao'))

    return render_template('patio/alerta_viatura.html', alerta_form=alerta_form)


@patio.route('/concluir_alerta/<int:alerta_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def concluir_alerta(alerta_id):
    alerta = AlertaViatura.query.get_or_404(alerta_id)
    alerta.status = "Resolvido"
    db.session.commit()
    flash('Alerta de viatura concluído com sucesso!', 'success')
    return redirect(url_for('patio.supervisao'))


@patio.route('/cancelar_alerta/<int:alerta_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Supervisor')
def cancelar_alerta(alerta_id):
    alerta = AlertaViatura.query.get_or_404(alerta_id)
    alerta.status = "Cancelado"
    db.session.commit()
    flash('Alerta de viatura cancelado com sucesso!', 'success')
    return redirect(url_for('patio.supervisao'))


@patio.route('/equipes', methods=['GET', 'POST'])
@login_required
def list_equipes():
    equipes = Equipe.query.all()
    return render_template('patio/list_equipes.html', equipes=equipes)

@patio.route('/equipe/create', methods=['GET', 'POST'])
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

@patio.route('/equipe/edit/<int:id>', methods=['GET', 'POST'])
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

@patio.route('/equipe/delete/<int:id>', methods=['POST'])
@login_required
def delete_equipe(id):
    equipe = Equipe.query.get_or_404(id)
    db.session.delete(equipe)
    db.session.commit()
    flash('Equipe excluída com sucesso!', 'success')
    return redirect(url_for('patio.list_equipes'))
