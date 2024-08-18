from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.models import CalendarEvent, WorkGroup
from datetime import datetime
from dateutil.parser import isoparse
import pytz
from . import bp as calendar
from .. import db
from app.auth.decorators import role_required

# Defina o fuso horário local
local_tz = pytz.timezone('America/Sao_Paulo')  # Ajuste conforme necessário

@calendar.route('/calendar')
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def calendar_view():
    workgroups = current_user.workgroups
    return render_template('calendar/calendar.html', workgroups=workgroups)

@calendar.route('/api/events', methods=['GET'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def get_events():
    workgroup_id = request.args.get('workgroup_id')
    if workgroup_id:
        events = CalendarEvent.query.filter_by(workgroup_id=workgroup_id).all()
    else:
        events = CalendarEvent.query.filter(CalendarEvent.workgroup_id.in_([wg.id for wg in current_user.workgroups])).all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'start': event.start.isoformat(),
        'end': event.end.isoformat() if event.end else None,
        'allDay': event.all_day,
        'backgroundColor': event.background_color,
        'borderColor': event.border_color,
        'textColor': event.text_color
    } for event in events])

@calendar.route('/api/events', methods=['POST'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def add_event():
    data = request.get_json()
    start = isoparse(data['start']).astimezone(local_tz)
    end = isoparse(data['end']).astimezone(local_tz) if data.get('end') else None

    event = CalendarEvent(
        title=data['title'],
        start=start,
        end=end,
        all_day=data.get('allDay', False),
        background_color=data.get('backgroundColor', '#0073b7'),
        border_color=data.get('borderColor', '#0073b7'),
        text_color=data.get('textColor', '#ffffff'),
        workgroup_id=data['workgroup_id']
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'status': 'success', 'id': event.id})

@calendar.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def update_event(event_id):
    data = request.get_json()
    event = CalendarEvent.query.get(event_id)
    if not event:
        return jsonify({'status': 'error', 'message': 'Evento não encontrado'}), 404

    start = isoparse(data['start']).astimezone(local_tz)
    end = isoparse(data['end']).astimezone(local_tz) if data.get('end') else None

    event.title = data['title']
    event.start = start
    event.end = end
    event.all_day = data.get('allDay', False)
    event.background_color = data.get('backgroundColor', '#0073b7')
    event.border_color = data.get('borderColor', '#0073b7')
    event.text_color = data.get('textColor', '#ffffff')
    db.session.commit()
    return jsonify({'status': 'success'})

@calendar.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
@role_required('Administrador', 'Assessor', 'Coordenador', 'Qualidade', 'Supervisor' )
def delete_event(event_id):
    event = CalendarEvent.query.get(event_id)
    if not event:
        return jsonify({'status': 'error', 'message': 'Evento não encontrado'}), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify({'status': 'success'})

@calendar.route('/dash_calendar')
@login_required
def dash_calendar():
    workgroups = current_user.workgroups
    return render_template('calendar/dash_calendar.html', workgroups=workgroups)

