from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField, SelectField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Local, Gestor, User, Role
from datetime import datetime
import pytz


brasilia_tz = pytz.timezone('America/Sao_Paulo')

def get_locais():
    return Local.query.all()

def get_gestores():
    return Gestor.query.all()

def get_user():
    return User.query.all()

class NcpsForm(FlaskForm):
    id = IntegerField('ID')
    data_hora_registro = DateTimeField('Data e Hora do Registro', format='%Y-%m-%dT%H:%M', default=datetime.now(brasilia_tz), validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    local = StringField('Local')
    local_padronizado = QuerySelectField('Local Padronizado', query_factory=get_locais, allow_blank=True, get_label='nome')
    id_ocorrencia = StringField('ID da Ocorrência')
    data_hora_ocorrencia = DateTimeField('Data e Hora da Ocorrência', [Optional()], format='%Y-%m-%dT%H:%M', default=None)
    dano = SelectField('Dano', choices=[('0', 'Aguardando análise'), ('1', 'Não'), ('2', 'Leve'), ('3', 'Moderado'), ('4', 'Grave'), ('5', 'Óbito')])
    classificacao_incidente = SelectField('Classificação do Incidente', choices=[('0', 'Aguardando análise'), ('1', 'Near miss'), ('2', 'Circunstância de risco'), ('3', 'Incidente ou evento sem dano'), ('4', 'Evento adverso')])
    sugestao = TextAreaField('Ação realizada / Sugestão')
    procedente = SelectField('Procedente', choices=[('0', 'Aguardando análise'), ('1', 'Analisando'), ('2', 'Sim'), ('3', 'Não'), ('4', 'Em parte')])
    gestor = QuerySelectField('Gestor', query_factory=get_gestores, allow_blank=True, get_label='nome')
    coordenador = QuerySelectField('Coordenador', query_factory=get_user, allow_blank=True, get_label='name')
    macroprocesso = SelectField('Macroprocesso', choices=[('0', 'Aguardando análise'), ('1', 'P1 - Abertura de chamdo'), ('2', 'P2 - Decisão técnica'), ('3', 'P3 - Empenho'), ('4', 'P4 - Deslocamento ao QTH'), ('5', 'P5 - Atendimento no local'), ('6', 'Contra-regulação'), ('7', 'P7 - Decisão gestora'), ('8', 'P8 - Deslocamento ao destino'), ('9', 'P9 - Transferência de cuidados'), ('10', 'Prontidão'), ('11', 'Administrativo'), ('12', 'Sistema'), ('99', 'Não se aplica')])
    seguranca = SelectField('Segurança do Paciente', choices=[('0', 'Aguardando análise'), ('1', 'Identificação do paciente'), ('2', 'Cuidado limpo e seguro'), ('3', 'Utilização de catéteres e sondas'), ('4', 'Procedimento seguro'), ('5', 'Administração segura de medicamentos e soluções'), ('6', 'Envolvimento do paciente com sua própria segurança'), ('7', 'Comunicação efetiva'), ('8', 'Prevenção de queda e acidente'), ('9', 'Prevenção de úlceras por pressão'), ('10', 'Segurança na utilização de tecnologia'), ('99', 'Não se aplica')])
    sentinela = SelectField('Evento Sentinela', choices=[('0', 'Aguardando análise'), ('1', 'Ato de violação intencional à prontidão'), ('2', 'Endereço errado em chamado prioritário'), ('3', 'Decisão técnica do MR inapropriada (apoio imediato de USA)'), ('4', 'Não empenho de recurso prioritário pelo RO'), ('5', 'Insubordinação às decisões da Central de Regulação'), ('6', 'Deslocamento inadequado com demora no percurso'), ('7', 'Contra-regulação inadequada, incoerente, distorcida ou ausente'), ('8', 'Administração de medicamentos de vigilância sem prescrição médica'), ('9', 'Intercorrência inesperada e crítica após medicação'), ('10', 'Intercorrência inesperada e crítica após procedimento'), ('11', 'Recusa coerente de paciente pelo primeiro destino'), ('12', 'Acidente de trânsito em atendimento'), ('13', 'Abandono de paciente'), ('14', 'Queda de paciente'), ('15', 'Atraso em situação tempo-dependente'), ('16', 'Acidente com material biológico ou pérfuro-cortante'), ('17', 'Agressão física à equipe'), ('18', 'Atendimento em cena insegura'), ('99', 'Não se aplica')])
    impacto = SelectField('Impacto', choices=[('0', 'Aguardando análise'), ('1', 'Alto'), ('2', 'Baixo')])
    probabilidade = SelectField('Probabilidade', choices=[('0', 'Aguardando análise'), ('1', 'Alto'), ('2', 'Baixo')])
    controle = SelectField('Controle', choices=[('0', 'Aguardando análise'), ('1', 'Alto'), ('2', 'Baixo')])
    causa = SelectField('Causa Raiz', choices=[('0', 'Aguardando análise'), ('1', 'Fatores do paciente'), ('2', 'Fatores da tarefa ou tecnologia'), ('3', 'Fatores individuais (pessoas)'), ('4', 'Fatores do time (equipe)'), ('5', 'Fatores do ambiente de trabalho'), ('6', 'Fatores organizacionais e gerenciais'), ('7', 'Fatores do contexto institucional')])
    plano = TextAreaField('Plano de Ação')
    acao = SelectField('Ação', choices=[('0', 'Aguardando análise'), ('1', 'Ações estruturais'), ('2', 'Ações construtivas'), ('3', 'Ações educacionais'), ('4', 'Ações disciplinares'), ('5', 'Ações administrativas')])
    prazo = DateTimeField('Prazo', [Optional()], format='%Y-%m-%d', default=None)
    status = SelectField('Status', choices=[('0', 'Aguardando análise da qualidade'), ('1', 'Analisando pelo coordenador'), ('2', 'Concluído Análise'), ('3', 'Arquivado'), ('4', 'Encaminhado ao gestor competente de outra instituição')], default=None)
    submit = SubmitField('Salvar')

class SearchForm(FlaskForm):
    id = IntegerField('ID do Ncps', validators=[DataRequired()])
    submit = SubmitField('Pesquisar')


class NcpsReportForm(FlaskForm):
    gestor = SelectField('Gestor', coerce=int, validators=[DataRequired()])
    start_date = DateTimeLocalField('Data/Hora Início', format='%Y-%m-%dT%H:%M', default=datetime.now(brasilia_tz), validators=[Optional()])
    end_date = DateTimeLocalField('Data/Hora Fim', format='%Y-%m-%dT%H:%M', default=datetime.now(brasilia_tz), validators=[Optional()])
    submit = SubmitField('Gerar Relatório')

    def __init__(self, *args, **kwargs):
        super(NcpsReportForm, self).__init__(*args, **kwargs)
        self.gestor.choices = [(g.id, g.nome) for g in Gestor.query.all()]