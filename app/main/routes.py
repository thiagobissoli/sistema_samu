from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import ControlePark, Previsao, CalendarEvent
from app.models import User, Viatura, ControlePark, Previsao, Local, Gestor, Ncps, Role, AlertaViatura
from datetime import datetime
from dateutil.parser import isoparse
import pytz
from . import bp as main
from .. import db
from ..utils import current_time_brasilia
import os
import csv

# Defina o fuso horário local
local_tz = pytz.timezone('America/Sao_Paulo')

@main.route('/')
@login_required
def index1():
    current_time = current_time_brasilia()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Filtrando os controles que têm hora_saida no dia atual
    controles = ControlePark.query.filter(ControlePark.hora_saida.is_(None)).all()
    previsoes = Previsao.query.filter_by(finalizacao=0).all()
    alertas = AlertaViatura.query.filter_by(status="Pendente").all()

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
            record.hora_entrada = local_tz.localize(record.hora_entrada)

    return render_template('main/index1.html', controles=controles, previsoes=previsoes, alertas=alertas, percentages=percentages, current_time=current_time)

@main.route('/index2')
@login_required
def index2():
    current_time = current_time_brasilia()
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Filtrando os controles que têm hora_saida no dia atual
    controles = ControlePark.query.filter(ControlePark.hora_entrada >= start_of_day, ControlePark.hora_entrada <= end_of_day).all()
    previsoes = Previsao.query.filter_by(finalizacao=0).all()

    # Calculando as porcentagens para o gráfico
    farmacia_count = sum(1 for controle in controles if controle.farmacia == 2)
    limpeza_count = sum(1 for controle in controles if controle.limpeza == 2)
    cme_count = sum(1 for controle in controles if controle.cme == 2)
    frota_count = sum(1 for controle in controles if controle.frota == 2)
    administrativo_count = sum(1 for controle in controles if controle.administrativo == 2)
    total_count = len(controles)

    percentages = {
        "farmacia": (farmacia_count / total_count) * 100 if total_count > 0 else 0,
        "limpeza": (limpeza_count / total_count) * 100 if total_count > 0 else 0,
        "cme": (cme_count / total_count) * 100 if total_count > 0 else 0,
        "frota": (frota_count / total_count) * 100 if total_count > 0 else 0,
        "administrativo": (administrativo_count / total_count) * 100 if total_count > 0 else 0,
    }

    for record in controles:
        if record.hora_entrada.tzinfo is None:
            record.hora_entrada = local_tz.localize(record.hora_entrada)
        if record.hora_saida and record.hora_saida.tzinfo is None:
            record.hora_saida = local_tz.localize(record.hora_saida)

    return render_template('main/index2.html', controles=controles, previsoes=previsoes, percentages=percentages, current_time=current_time)


def import_all_from_csv(session, input_directory):
    model_mapping = {
        'user': User,
        'viatura': Viatura,
        'controlepark': ControlePark,
        'previsao': Previsao,
        'local': Local,
        'gestor': Gestor,
        'ncps': Ncps
    }

    for filename, model in model_mapping.items():
        input_file = f"{input_directory}/{filename}.csv"
        if not os.path.exists(input_file):
            print(f"Arquivo {input_file} não encontrado. Pulando.")
            continue

        with open(input_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                instance = model()
                for column in model.__table__.columns:
                    value = row.get(column.name, None)
                    setattr(instance, column.name, value)

                session.add(instance)

        session.commit()
        print(f"Dados importados com sucesso para a tabela {model.__tablename__}")

@main.route('/import', methods=['POST'])
@login_required
def import_data():
    input_directory = 'migration_data'
    session = db.session
    import_all_from_csv(session, input_directory)
    return jsonify({"message": "Dados importados com sucesso!"})
