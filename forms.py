from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=4, max=100)])
    remember = BooleanField("Recordarme")


class RegisterClienteForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Length(max=30)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6, max=100)])


class CreateStaffForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6, max=100)])
    rol = SelectField("Rol", choices=[("EMPLEADO","Empleado/Vendedor"), ("ADMIN","Admin")], validators=[DataRequired()])
