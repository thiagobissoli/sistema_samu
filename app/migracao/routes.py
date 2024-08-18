from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as migracao
from ..models import Ncps, User, Local, Gestor
from .. import db
import csv
import os
from sqlalchemy.exc import IntegrityError

@migracao.route('/ncps', methods=['GET'])
@login_required
def ncps():
    ncps_list = Ncps.query.all()
    return render_template('migracao/ncps.html', ncps_list=ncps_list)

@migracao.route('/import_ncps', methods=['POST'])
@login_required
def import_ncps():
    return handle_import(Ncps, 'migracao.ncps')

@migracao.route('/users', methods=['GET'])
@login_required
def users():
    users_list = User.query.all()
    return render_template('migracao/users.html', users_list=users_list)

def convert_to_boolean(value):
    """Converte uma string como 'True' ou 'False' em um valor booleano."""
    if value is None or value == '':
        return None
    return value.lower() == 'true'

def extract_username_from_email(email):
    """Extrai o trecho antes do '@' do email para usar como username."""
    if email:
        return email.split('@')[0]
    return None


def generate_unique_username(base_username):
    """Gera um username único adicionando sufixos numéricos se necessário."""
    username = base_username
    counter = 1
    while User.query.filter_by(username=username).first() is not None:
        username = f"{base_username}{counter}"
        counter += 1
    return username

@migracao.route('/import_users', methods=['POST'])
def import_users():
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('migracao.users'))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('migracao.users'))

    # Verifica se o arquivo é um CSV
    if not file.filename.endswith('.csv'):
        flash('O arquivo precisa ser um CSV', 'danger')
        return redirect(url_for('migracao.users'))

    # Caminho para salvar o arquivo temporariamente
    filepath = os.path.join('/tmp', file.filename)
    file.save(filepath)

    # Leitura do CSV e inserção no banco de dados
    try:
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                existing_user = User.query.get(row['id'])
                if existing_user:
                    # Se já existe, ignorar ou atualizar (dependendo do seu caso de uso)
                    flash(f'O usuário com ID {row["id"]} já existe e foi ignorado.', 'warning')
                    continue

                user = User()
                for column in User.__table__.columns:
                    value = row.get(column.name, None)

                    # Converter 'is_active' para booleano
                    if column.name == 'is_active':
                        value = convert_to_boolean(value)

                    # Se o campo 'username' estiver vazio, gerar a partir do email
                    if column.name == 'username':
                        if value is None or value == '':
                            base_username = extract_username_from_email(row.get('email'))
                            value = generate_unique_username(base_username)
                        else:
                            value = generate_unique_username(value)

                    # Definir valores vazios como None
                    if value == '':
                        value = None

                    setattr(user, column.name, value)

                db.session.add(user)

            db.session.commit()
        flash('Dados importados com sucesso!', 'success')
    except IntegrityError as e:
        db.session.rollback()
        flash(f'Erro de integridade: {str(e.orig)}', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao importar os dados: {str(e)}', 'danger')
    finally:
        # Remover o arquivo temporário
        os.remove(filepath)

    return redirect(url_for('migracao.users'))



@migracao.route('/locais', methods=['GET'])
@login_required
def locais():
    locais_list = Local.query.all()
    return render_template('migracao/locais.html', locais_list=locais_list)

@migracao.route('/import_locais', methods=['POST'])
@login_required
def import_locais():
    return handle_import(Local, 'migracao.locais')

@migracao.route('/gestores', methods=['GET'])
@login_required
def gestores():
    gestores_list = Gestor.query.all()
    return render_template('migracao/gestores.html', gestores_list=gestores_list)

@migracao.route('/import_gestores', methods=['POST'])
@login_required
def import_gestores():
    return handle_import(Gestor, 'migracao.gestores')

def handle_import(model, redirect_route):
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for(redirect_route))

    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for(redirect_route))

    if not file.filename.endswith('.csv'):
        flash('O arquivo precisa ser um CSV', 'danger')
        return redirect(url_for(redirect_route))

    filepath = os.path.join('/tmp', file.filename)
    file.save(filepath)

    try:
        with open(filepath, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                existing_record = model.query.get(row['id'])
                if existing_record:
                    flash(f'O registro com ID {row["id"]} já existe e foi ignorado.', 'warning')
                    continue

                record = model()
                for column in model.__table__.columns:
                    value = row.get(column.name, None)
                    if value == '':
                        value = None
                    setattr(record, column.name, value)

                db.session.add(record)

            db.session.commit()
        flash('Dados importados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ocorreu um erro ao importar os dados: {str(e)}', 'danger')
    finally:
        os.remove(filepath)

    return redirect(url_for(redirect_route))
