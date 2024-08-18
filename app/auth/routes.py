from flask import render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from . import bp as auth
from .forms import LoginForm, CreateUserForm, EditUserForm, RoleForm, SelfUserForm, ResetPassForm, ForgotPasswordForm
from ..models import User, Role
from .. import db, mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_mail import Message
from werkzeug.security import generate_password_hash
from .decorators import role_required


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Login inválido.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=True)
        session['user_id'] = user.id
        return redirect(url_for('main.index1'))

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    logout_user()
    return redirect(url_for('main.index1'))

@auth.route('/list_users')
@login_required
@role_required('Administrador')
def list_users():
    users = User.query.filter_by(deleted=False).all()
    return render_template('auth/list_users.html', users=users)


@auth.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.name = form.name.data
        user.email = form.email.data
        user.role_id = form.role.data
        user.hospital_id = form.hospital.data if form.hospital.data != 0 else None
        user.is_active = form.is_active.data
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('auth.list_users'))
    return render_template('auth/edit_user.html', form=form, user=user)

@auth.route('/user/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data,
                        name=form.name.data,
                        email=form.email.data,
                        is_active=form.is_active.data,
                        hospital_id=form.hospital.data if form.hospital.data != 0 else None)
        new_user.set_password(form.password.data)
        new_user.role_id = form.role.data
        db.session.add(new_user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('auth.list_users'))
    return render_template('auth/create_user.html', form=form)

@auth.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrador')
def delete_user(id):
    user = User.query.get_or_404(id)
    user.deleted = True
    db.session.commit()
    flash('Usuário marcado como excluído com sucesso!', 'success')
    return redirect(url_for('auth.list_users'))

@auth.route('/roles')
@login_required
@role_required('Administrador')
def list_roles():
    roles = Role.query.filter_by(deleted=False).all()
    return render_template('auth/list_roles.html', roles=roles)

@auth.route('/role/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data)
        db.session.add(role)
        db.session.commit()
        flash('Perfil criado com sucesso!', 'success')
        return redirect(url_for('auth.list_roles'))
    return render_template('auth/create_role.html', form=form)

@auth.route('/role/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrador')
def edit_role(id):
    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.list_roles'))
    return render_template('auth/edit_role.html', form=form, role=role)

@auth.route('/role/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Administrador')
def delete_role(id):
    role = Role.query.get_or_404(id)
    role.deleted = True
    db.session.commit()
    flash('Perfil marcado como excluído com sucesso!', 'success')
    return redirect(url_for('auth.list_roles'))

@auth.route('/self_user', methods=['GET', 'POST'])
@login_required
def self_user():
    user = current_user
    form = SelfUserForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Seus dados foram atualizados com sucesso!', 'success')
        return redirect(url_for('main.index1'))
    return render_template('auth/self_user.html', form=form, user=user)

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='reset-password')
            msg = Message('Redefinição de Senha do Sistema SAMU 192 ES', sender='noreply@yourdomain.com', recipients=[user.email])
            msg.body = f'Clique no link para redefinir a senha do usuário {user.username}: {url_for("auth.reset_password", token=token, _external=True)}'
            mail.send(msg)
            flash('Um email foi enviado com instruções para redefinir sua senha.', 'info')
            return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)
    except (SignatureExpired, BadTimeSignature):
        flash('O token é inválido ou expirou.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPassForm()
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Endereço de email inválido!', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if form.validate_on_submit():
        try:
            print(f"Atualizando senha para o usuário: {user.email}")  # Log de depuração
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user.password_hash = hashed_password
            db.session.commit()
            flash('Sua senha foi atualizada!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Erro ao atualizar a senha: {e}', 'danger')
            print(f"Erro ao atualizar a senha: {e}")  # Log de depuração

    return render_template('auth/reset_password.html', form=form)


