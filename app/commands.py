# /app/commands.py
from flask import current_app
from flask.cli import with_appcontext
import click

@click.command(name='init_roles')
@with_appcontext
def init_roles():
    from . import ensure_roles_exist, ensure_admin_user
    ensure_roles_exist()
    ensure_admin_user()
    click.echo('Roles and admin user have been initialized')
