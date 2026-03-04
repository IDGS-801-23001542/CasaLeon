from flask_sqlalchemy import SQLAlchemy

import datetime

db = SQLAlchemy()


class Rol(db.Model):
    __tablename__ = "Rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)  # ADMIN / EMPLEADO
    descripcion = db.Column(db.String(120), nullable=False)


class Usuario(db.Model):
    __tablename__ = "Usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("Rol.id_rol"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Integer, nullable=False, default=1)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    rol = db.relationship("Rol")


class Cliente(db.Model):
    __tablename__ = "Cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    rfc = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    telefono = db.Column(db.String(30))
    calle = db.Column(db.String(120))
    numero = db.Column(db.String(20))
    colonia = db.Column(db.String(120))
    ciudad = db.Column(db.String(80))
    estado = db.Column(db.String(80))
    pais = db.Column(db.String(80))
    cp = db.Column(db.String(10))

    password_hash = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    activo = db.Column(db.Integer, nullable=False, default=1)


class AuthToken(db.Model):
    __tablename__ = "AuthToken"
    id_token = db.Column(db.Integer, primary_key=True)
    subject_type = db.Column(db.Enum("USUARIO", "CLIENTE"), nullable=False)
    subject_id = db.Column(db.Integer, nullable=False)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Integer, nullable=False, default=0)
    user_agent = db.Column(db.String(255))
    ip_addr = db.Column(db.String(45))
