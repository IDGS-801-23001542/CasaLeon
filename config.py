class Config(object):
    SECRET_KEY = "CasaLeon_ClaveSecreta_Cambiala"
    SESSION_COOKIE_SECURE = False  # en producción: True con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/fabrica_pieles2'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRES_HOURS = 8
