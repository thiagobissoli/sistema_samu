import os


class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@localhost/samu2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
#    MAIL_USERNAME = 'thiagosbissoli@gmail.com'
    MAIL_USERNAME = 'sistemawebsamu@gmail.com'
#    MAIL_PASSWORD = 'zlxhwbthdklqzdkb' # thiagobissoli
    MAIL_PASSWORD = 'nlji ikwy qmoh lupw' # sistema samu