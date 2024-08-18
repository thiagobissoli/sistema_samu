from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .forms import WorkGroupForm, AddUserToWorkGroupForm
from app.models import WorkGroup, User
from app import db
from . import bp as workgroup
from app.auth.decorators import role_required

@workgroup.route('/')
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def list_workgroups():
    workgroups = WorkGroup.query.all()
    return render_template('workgroup/list_workgroups.html', workgroups=workgroups)

@workgroup.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def create_workgroup():
    form = WorkGroupForm()
    if form.validate_on_submit():
        workgroup = WorkGroup(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(workgroup)
        db.session.commit()

        # Automatically add the creator to the workgroup
        workgroup.users.append(current_user)
        db.session.commit()

        flash('Grupo de trabalho criado com sucesso!', 'success')
        return redirect(url_for('workgroup.list_workgroups'))
    return render_template('workgroup/create_workgroup.html', form=form)

@workgroup.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def edit_workgroup(id):
    workgroup = WorkGroup.query.get_or_404(id)
    form = WorkGroupForm(obj=workgroup)
    if form.validate_on_submit():
        workgroup.name = form.name.data
        workgroup.description = form.description.data
        db.session.commit()

        flash('Grupo de trabalho atualizado com sucesso!', 'success')
        return redirect(url_for('workgroup.list_workgroups'))
    return render_template('workgroup/edit_workgroup.html', form=form, workgroup=workgroup)


@workgroup.route('/<int:id>/view', methods=['GET'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def view_workgroup(id):
    workgroup = WorkGroup.query.get_or_404(id)
    return render_template('workgroup/view_workgroup.html', workgroup=workgroup)

@workgroup.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def delete_workgroup(id):
    workgroup = WorkGroup.query.get_or_404(id)
    db.session.delete(workgroup)
    db.session.commit()
    flash('Grupo de trabalho excluído com sucesso!', 'success')
    return redirect(url_for('workgroup.list_workgroups'))

@workgroup.route('/<int:id>/add_users', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def add_users_workgroup(id):
    workgroup = WorkGroup.query.get_or_404(id)
    form = AddUserToWorkGroupForm()
    form.users.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    if form.validate_on_submit():
        for user_id in form.users.data:
            user = User.query.get(user_id)
            if user not in workgroup.users:
                workgroup.users.append(user)
        db.session.commit()
        flash('Usuários adicionados ao grupo de trabalho!', 'success')
        return redirect(url_for('workgroup.view_workgroup', id=id))
    return render_template('workgroup/add_users_workgroup.html', form=form, workgroup=workgroup)

@workgroup.route('/<int:workgroup_id>/remove_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Coordenador', 'Qualidade')
def remove_user_from_workgroup(workgroup_id, user_id):
    workgroup = WorkGroup.query.get_or_404(workgroup_id)
    user = User.query.get_or_404(user_id)
    if user in workgroup.users:
        workgroup.users.remove(user)
        db.session.commit()
        flash('Usuário removido do grupo de trabalho!', 'success')
    return redirect(url_for('workgroup.view_workgroup', id=workgroup_id))
