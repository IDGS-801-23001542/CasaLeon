import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError


def validar_rfc(form, field):
    if not field.data:
        return

    rfc = field.data.strip().upper()

    patron = r"^([A-ZÑ&]{3,4})\d{6}[A-Z0-9]{3}$"

    if not re.match(patron, rfc):
        raise ValidationError("El RFC no tiene un formato válido")

    fecha = rfc[3:9] if len(rfc) == 12 else rfc[4:10]

    try:
        month = int(fecha[2:4])
        day = int(fecha[4:6])

        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError()

    except Exception:
        raise ValidationError("El RFC contiene una fecha inválida")


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


class ProveedorForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(min=3, max=150, message="El nombre debe tener entre 3 y 150 caracteres"),
        ],
    )

    rfc = StringField(
        "RFC",
        validators=[
            Optional(),
            Length(max=13, message="El RFC no puede exceder 13 caracteres"),
            validar_rfc,
        ],
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Ingresa un correo válido"),
            Length(max=120, message="El correo no puede exceder 120 caracteres"),
        ],
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Length(max=30, message="El teléfono no puede exceder 30 caracteres"),
        ],
    )

    calle = StringField(
        "Calle",
        validators=[
            Optional(),
            Length(max=120, message="La calle no puede exceder 120 caracteres"),
        ],
    )

    numero = StringField(
        "Número",
        validators=[
            Optional(),
            Length(max=20, message="El número no puede exceder 20 caracteres"),
        ],
    )

    colonia = StringField(
        "Colonia",
        validators=[
            Optional(),
            Length(max=120, message="La colonia no puede exceder 120 caracteres"),
        ],
    )

    ciudad = StringField(
        "Ciudad",
        validators=[
            Optional(),
            Length(max=80, message="La ciudad no puede exceder 80 caracteres"),
        ],
    )

    estado = StringField(
        "Estado",
        validators=[
            Optional(),
            Length(max=80, message="El estado no puede exceder 80 caracteres"),
        ],
    )

    pais = StringField(
        "País",
        validators=[
            Optional(),
            Length(max=80, message="El país no puede exceder 80 caracteres"),
        ],
    )

    cp = StringField(
        "Código Postal",
        validators=[
            Optional(),
            Length(max=10, message="El código postal no puede exceder 10 caracteres"),
        ],
    )


class ProductoForm(FlaskForm):
    id_categoria_producto = SelectField(
        "Categoría",
        coerce=int,
        validators=[DataRequired(message="La categoría es requerida")],
        choices=[],
    )

    sku = StringField(
        "SKU",
        validators=[
            Optional(),
            Length(max=40, message="El SKU no puede exceder 40 caracteres"),
        ],
    )

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(min=3, max=120, message="El nombre debe tener entre 3 y 120 caracteres"),
        ],
    )

    descripcion = StringField(
        "Descripción",
        validators=[
            Optional(),
            Length(max=255, message="La descripción no puede exceder 255 caracteres"),
        ],
    )

    precio_venta = DecimalField(
        "Precio de Venta",
        validators=[
            DataRequired(message="El precio de venta es requerido"),
            NumberRange(min=0, message="El precio debe ser mayor o igual a 0"),
        ],
    )

    stock_actual = DecimalField(
        "Stock Actual",
        validators=[
            DataRequired(message="El stock actual es requerido"),
            NumberRange(min=0, message="El stock debe ser mayor o igual a 0"),
        ],
    )

    costo_unit_prom = DecimalField(
        "Costo Unitario Promedio",
        validators=[
            DataRequired(message="El costo unitario es requerido"),
            NumberRange(min=0, message="El costo debe ser mayor o igual a 0"),
        ],
    )