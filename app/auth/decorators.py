from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user

def role_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            user_role = current_user.role.name  # Acessa diretamente o nome do role
            if user_role not in required_roles:
                flash('O usuário não possui perfil autorizado para o acesso a esta função!', 'error')
                return redirect(url_for('main.index1'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
