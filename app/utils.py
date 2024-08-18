from datetime import datetime
import pytz

def current_time_brasilia():
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz)
