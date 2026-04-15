import os
import cloudinary


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "CasaLeon_ClaveSecreta_Cambiala")
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "casaleon_mongo")

    MAIL_SERVER = (os.getenv("MAIL_SERVER") or "smtp.gmail.com").strip()
    MAIL_PORT = int((os.getenv("MAIL_PORT") or "587").strip())
    MAIL_USE_TLS = (os.getenv("MAIL_USE_TLS") or "True").strip() == "True"
    MAIL_USE_SSL = (os.getenv("MAIL_USE_SSL") or "False").strip() == "True"
    MAIL_USERNAME = (os.getenv("MAIL_USERNAME") or "").strip()
    MAIL_PASSWORD = (os.getenv("MAIL_PASSWORD") or "").strip()
    MAIL_DEFAULT_SENDER = (os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME).strip()

    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "casaleon-email-salt")
    TOTP_ISSUER = os.getenv("TOTP_ISSUER", "Casa Leon")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@127.0.0.1/fabrica_pieles2"
    )
    TOKEN_EXPIRES_MINUTES = 10
    REMEMBER_COOKIE_DAYS = 7


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)