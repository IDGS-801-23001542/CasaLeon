from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Contraseña", validators=[DataRequired(), Length(min=4, max=100)]
    )
    remember = BooleanField("Recordarme")


class RegisterClienteForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Length(max=30)])
    password = PasswordField(
        "Contraseña", validators=[DataRequired(), Length(min=6, max=100)]
    )


class CreateStaffForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Contraseña", validators=[DataRequired(), Length(min=6, max=100)]
    )
    rol = SelectField(
        "Rol",
        choices=[("EMPLEADO", "Empleado/Vendedor"), ("ADMIN", "Admin")],
        validators=[DataRequired()],
    )

class UsuarioForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(
                min=3, max=120, message="El nombre debe tener entre 3 y 120 caracteres"
            ),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El correo es requerido"),
            Email(message="Ingresa un correo válido"),
            Length(max=120, message="El correo no puede exceder 120 caracteres"),
        ],
    )

    rol = SelectField(
        "Rol",
        coerce=int,
        validators=[
            DataRequired(message="El rol es requerido"),
        ],
        choices=[],
    )

    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[
            DataRequired(message="El estado es requerido"),
        ],
        choices=[
            (1, "Activo"),
            (0, "Inactivo"),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            Optional(),
            Length(
                min=8,
                max=128,
                message="La contraseña debe tener entre 8 y 128 caracteres",
            ),
        ],
    )
