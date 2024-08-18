from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from . import bp as kanban
from .forms import ProjectForm, ColumnForm, TaskForm, AddUserToProjectForm
from ..models import KanbanProject, KanbanColumn, KanbanTask, User
from .. import db
from app.auth.decorators import role_required

@kanban.route('/projects')
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def list_projects():
    projects = current_user.projects
    return render_template('kanban/list_projects.html', projects=projects)

@kanban.route('/project/<int:project_id>')
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def view_project(project_id):
    project = KanbanProject.query.get_or_404(project_id)
    return render_template('kanban/view_project.html', project=project)

@kanban.route('/project/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = KanbanProject(name=form.name.data, description=form.description.data)
        project.users.append(current_user)  # Adiciona o usuário atual ao projeto
        db.session.add(project)
        db.session.commit()
        flash('Projeto criado com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=project.id))
    return render_template('kanban/create_project.html', form=form)

@kanban.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def edit_project(project_id):
    project = KanbanProject.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=project.id))
    return render_template('kanban/edit_project.html', form=form, project=project)


@kanban.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def delete_project(project_id):
    project = KanbanProject.query.get_or_404(project_id)
    if current_user not in project.users:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash('Projeto Kanban deletado com sucesso!', 'success')
    return redirect(url_for('kanban.list_projects'))

@kanban.route('/project/<int:project_id>/add_user', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def add_user_to_project(project_id):
    project = KanbanProject.query.get_or_404(project_id)
    if current_user not in project.users:
        abort(403)
    form = AddUserToProjectForm()
    form.user_id.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if user:
            project.users.append(user)
            db.session.commit()
            flash('Usuário adicionado ao projeto!', 'success')
        else:
            flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('kanban.add_user_to_project', project_id=project_id))
    return render_template('kanban/add_user_to_project.html', form=form, project=project)

@kanban.route('/project/<int:project_id>/remove_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def remove_user_from_project(project_id, user_id):
    project = KanbanProject.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    if current_user not in project.users:
        abort(403)
    if user in project.users:
        project.users.remove(user)
        db.session.commit()
        flash('Usuário removido do projeto com sucesso!', 'success')
    else:
        flash('Usuário não está no projeto!', 'danger')
    return redirect(url_for('kanban.add_user_to_project', project_id=project_id))


@kanban.route('/column/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def create_column(project_id):
    form = ColumnForm()
    if form.validate_on_submit():
        column = KanbanColumn(name=form.name.data, project_id=project_id)
        db.session.add(column)
        db.session.commit()
        flash('Coluna criada com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=project_id))
    return render_template('kanban/create_column.html', form=form)

@kanban.route('/column/<int:column_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def edit_column(column_id):
    column = KanbanColumn.query.get_or_404(column_id)
    form = ColumnForm(obj=column)
    if form.validate_on_submit():
        column.name = form.name.data
        db.session.commit()
        flash('Coluna atualizada com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=column.project_id))
    return render_template('kanban/edit_column.html', form=form, column=column)


@kanban.route('/column/<int:column_id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def delete_column(column_id):
    column = KanbanColumn.query.get_or_404(column_id)
    project_id = column.project_id
    db.session.delete(column)
    db.session.commit()
    flash('Coluna deletada com sucesso!', 'success')
    return redirect(url_for('kanban.view_project', project_id=project_id))


@kanban.route('/task/create/<int:column_id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def create_task(column_id):
    form = TaskForm()
    form.responsible_id.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    form.requester_id.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    if form.validate_on_submit():
        task = KanbanTask(
            title=form.title.data,
            description=form.description.data,
            responsible_id=form.responsible_id.data,
            requester_id=form.requester_id.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            column_id=column_id
        )
        db.session.add(task)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=task.column.project_id))
    return render_template('kanban/create_task.html', form=form)

@kanban.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def edit_task(task_id):
    task = KanbanTask.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    form.responsible_id.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    form.requester_id.choices = [(user.id, user.name) for user in User.query.order_by('name')]
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.responsible_id = form.responsible_id.data
        task.requester_id = form.requester_id.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('kanban.view_project', project_id=task.column.project_id))
    return render_template('kanban/edit_task.html', form=form, task=task)

@kanban.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def delete_task(task_id):
    task = KanbanTask.query.get_or_404(task_id)
    project_id = task.column.project_id
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa deletada com sucesso!', 'success')
    return redirect(url_for('kanban.view_project', project_id=project_id))

@kanban.route('/kanban/move_task', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def move_task():
    data = request.get_json()
    task_id = data.get('task_id')
    new_column_id = data.get('column_id')

    task = KanbanTask.query.get(task_id)
    if task:
        task.column_id = new_column_id
        db.session.commit()
        return jsonify({'message': 'Task moved successfully'}), 200
    return jsonify({'message': 'Task not found'}), 404