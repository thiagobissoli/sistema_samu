from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import bp as hospital
from .forms import HospitalForm
from ..models import Hospital
from .. import db
from app.auth.decorators import role_required


@hospital.route('/hospitais')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def list_hospitais():
    hospitais = Hospital.query.all()
    return render_template('hospital/list_hospitais.html', hospitais=hospitais)

@hospital.route('/hospital/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def create_hospital():
    form = HospitalForm()
    if form.validate_on_submit():
        new_hospital = Hospital(nome=form.nome.data, leitos=form.leitos.data)
        db.session.add(new_hospital)
        db.session.commit()
        flash('Hospital criado com sucesso!', 'success')
        return redirect(url_for('hospital.list_hospitais'))
    return render_template('hospital/create_hospital.html', form=form)

@hospital.route('/hospital/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def edit_hospital(id):
    hospital = Hospital.query.get_or_404(id)
    form = HospitalForm(obj=hospital)
    if form.validate_on_submit():
        hospital.nome = form.nome.data
        hospital.leitos = form.leitos.data
        db.session.commit()
        flash('Hospital atualizado com sucesso!', 'success')
        return redirect(url_for('hospital.list_hospitais'))
    return render_template('hospital/edit_hospital.html', form=form)

@hospital.route('/hospital/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_hospital(id):
    hospital = Hospital.query.get_or_404(id)
    db.session.delete(hospital)
    db.session.commit()
    flash('Hospital deletado com sucesso!', 'success')
    return redirect(url_for('hospital.list_hospitais'))

