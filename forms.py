import re
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectField,
    TextAreaField,
    DecimalField,
    FileField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    Length,
    Optional,
    NumberRange,
    ValidationError,
    Regexp,
    EqualTo,
)

from flask_wtf.file import FileAllowed


def validar_rfc(form, field):
    if not field.data:
        return

    rfc = "".join((field.data or "").strip().upper().split())
    field.data = rfc

    patron = r"^([A-ZÑ&]{3,4})\d{6}[A-Z0-9]{3}$"
    if not re.match(patron, rfc):
        raise ValidationError(
            "RFC inválido. Ejemplos: ABC010203AB1 (moral) o ABCD010203AB1 (física)."
        )

    fecha = rfc[3:9] if len(rfc) == 12 else rfc[4:10]
    try:
        month = int(fecha[2:4])
        day = int(fecha[4:6])
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError()
    except Exception:
        raise ValidationError("El RFC contiene una fecha inválida. Usa formato AAMMDD.")


def _has_letters(value: str) -> bool:
    return any(char.isalpha() for char in value)


def _normalize_spaces(value: str) -> str:
    return " ".join((value or "").strip().split())


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo válido."),
            Length(max=120, message="El correo no puede exceder 120 caracteres."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(
                min=6,
                max=100,
                message="La contraseña debe tener entre 6 y 100 caracteres.",
            ),
        ],
    )
    remember = BooleanField("Recordarme")

    def validate_email(self, field):
        field.data = _normalize_spaces(field.data).lower()

    def validate_password(self, field):
        field.data = (field.data or "").strip()
        if not field.data:
            raise ValidationError("La contraseña no puede estar vacía.")


class RegisterClienteForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=2,
                max=150,
                message="El nombre debe tener entre 2 y 150 caracteres.",
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El nombre solo puede contener letras y espacios.",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo válido."),
            Length(max=120, message="El correo no puede exceder 120 caracteres."),
        ],
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Length(
                min=10,
                max=15,
                message="El teléfono debe tener entre 10 y 15 caracteres.",
            ),
            Regexp(
                r"^\+?[0-9\s\-]+$",
                message="El teléfono solo puede contener números, espacios, guiones y un + opcional.",
            ),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(
                min=6,
                max=100,
                message="La contraseña debe tener entre 6 y 100 caracteres.",
            ),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d).+$",
                message="La contraseña debe contener al menos una letra y un número.",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa un nombre válido.")

    def validate_email(self, field):
        field.data = _normalize_spaces(field.data).lower()

    def validate_telefono(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)
            digitos = "".join(char for char in field.data if char.isdigit())
            if len(digitos) < 10 or len(digitos) > 15:
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")

    def validate_password(self, field):
        field.data = (field.data or "").strip()
        if " " in field.data:
            raise ValidationError("La contraseña no debe contener espacios.")

    def validate_confirm_password(self, field):
        field.data = (field.data or "").strip()


class CheckoutForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=2, max=150, message="El nombre debe tener entre 2 y 150 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El nombre solo puede contener letras y espacios.",
            ),
        ],
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Length(
                min=10,
                max=15,
                message="El teléfono debe tener entre 10 y 15 caracteres.",
            ),
            Regexp(
                r"^\+?[0-9\s\-]+$",
                message="El teléfono solo puede contener números, espacios, guiones y un + opcional.",
            ),
        ],
    )
    calle = StringField(
        "Calle",
        validators=[
            DataRequired(message="La calle es obligatoria."),
            Length(
                min=3, max=120, message="La calle debe tener entre 3 y 120 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\.\-#]+$",
                message="La calle contiene caracteres no permitidos.",
            ),
        ],
    )
    numero = StringField(
        "Número",
        validators=[
            DataRequired(message="El número es obligatorio."),
            Length(
                min=1, max=20, message="El número debe tener entre 1 y 20 caracteres."
            ),
            Regexp(
                r"^[A-Za-z0-9\s\-#]+$",
                message="El número contiene caracteres no permitidos.",
            ),
        ],
    )
    colonia = StringField(
        "Colonia",
        validators=[
            DataRequired(message="La colonia es obligatoria."),
            Length(
                min=2,
                max=120,
                message="La colonia debe tener entre 2 y 120 caracteres.",
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\.\-#]+$",
                message="La colonia contiene caracteres no permitidos.",
            ),
        ],
    )
    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(
                min=2, max=80, message="La ciudad debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="La ciudad solo puede contener letras y espacios.",
            ),
        ],
    )
    estado = StringField(
        "Estado",
        validators=[
            DataRequired(message="El estado es obligatorio."),
            Length(
                min=2, max=80, message="El estado debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El estado solo puede contener letras y espacios.",
            ),
        ],
    )
    pais = StringField(
        "País",
        validators=[
            DataRequired(message="El país es obligatorio."),
            Length(
                min=2, max=80, message="El país debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El país solo puede contener letras y espacios.",
            ),
        ],
    )
    cp = StringField(
        "Código postal",
        validators=[
            DataRequired(message="El código postal es obligatorio."),
            Length(
                min=5,
                max=10,
                message="El código postal debe tener entre 5 y 10 caracteres.",
            ),
            Regexp(
                r"^[0-9\-]+$",
                message="El código postal solo puede contener números y guiones.",
            ),
        ],
    )
    notas = TextAreaField(
        "Notas",
        validators=[
            Optional(),
            Length(max=255, message="Las notas no pueden exceder 255 caracteres."),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\.\,\-\#\(\)]*$",
                message="Las notas contienen caracteres no permitidos.",
            ),
        ],
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa un nombre válido.")

    def validate_telefono(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)
            digitos = "".join(char for char in field.data if char.isdigit())
            if len(digitos) < 10 or len(digitos) > 15:
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")

    def validate_calle(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa una calle válida.")

    def validate_numero(self, field):
        field.data = _normalize_spaces(field.data)

    def validate_colonia(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa una colonia válida.")

    def validate_ciudad(self, field):
        field.data = _normalize_spaces(field.data)

    def validate_estado(self, field):
        field.data = _normalize_spaces(field.data)

    def validate_pais(self, field):
        field.data = _normalize_spaces(field.data)

    def validate_cp(self, field):
        field.data = _normalize_spaces(field.data)


class UpdateClienteForm(FlaskForm):
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=2, max=150, message="El nombre debe tener entre 2 y 150 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El nombre solo puede contener letras y espacios.",
            ),
        ],
    )
    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Length(
                min=10,
                max=15,
                message="El teléfono debe tener entre 10 y 15 caracteres.",
            ),
            Regexp(
                r"^\+?[0-9\s\-]+$",
                message="El teléfono solo puede contener números, espacios, guiones y un + opcional.",
            ),
        ],
    )
    calle = StringField(
        "Calle",
        validators=[
            Optional(),
            Length(
                min=3, max=120, message="La calle debe tener entre 3 y 120 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\.\-#]*$",
                message="La calle contiene caracteres no permitidos.",
            ),
        ],
    )
    numero = StringField(
        "Número",
        validators=[
            Optional(),
            Length(
                min=1, max=20, message="El número debe tener entre 1 y 20 caracteres."
            ),
            Regexp(
                r"^[A-Za-z0-9\s\-#]*$",
                message="El número contiene caracteres no permitidos.",
            ),
        ],
    )
    colonia = StringField(
        "Colonia",
        validators=[
            Optional(),
            Length(
                min=2,
                max=120,
                message="La colonia debe tener entre 2 y 120 caracteres.",
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s\.\-#]*$",
                message="La colonia contiene caracteres no permitidos.",
            ),
        ],
    )
    ciudad = StringField(
        "Ciudad",
        validators=[
            Optional(),
            Length(
                min=2, max=80, message="La ciudad debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]*$",
                message="La ciudad solo puede contener letras y espacios.",
            ),
        ],
    )
    estado = StringField(
        "Estado",
        validators=[
            Optional(),
            Length(
                min=2, max=80, message="El estado debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]*$",
                message="El estado solo puede contener letras y espacios.",
            ),
        ],
    )
    pais = StringField(
        "País",
        validators=[
            Optional(),
            Length(
                min=2, max=80, message="El país debe tener entre 2 y 80 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]*$",
                message="El país solo puede contener letras y espacios.",
            ),
        ],
    )
    cp = StringField(
        "Código postal",
        validators=[
            Optional(),
            Length(
                min=5,
                max=10,
                message="El código postal debe tener entre 5 y 10 caracteres.",
            ),
            Regexp(
                r"^[0-9\-]*$",
                message="El código postal solo puede contener números y guiones.",
            ),
        ],
    )
    current_password = PasswordField(
        "Contraseña actual",
        validators=[
            Optional(),
            Length(
                min=6,
                max=100,
                message="La contraseña actual debe tener entre 6 y 100 caracteres.",
            ),
        ],
    )
    new_password = PasswordField(
        "Nueva contraseña",
        validators=[
            Optional(),
            Length(
                min=6,
                max=100,
                message="La nueva contraseña debe tener entre 6 y 100 caracteres.",
            ),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d).*$",
                message="La nueva contraseña debe contener al menos una letra y un número.",
            ),
        ],
    )
    confirm_new_password = PasswordField(
        "Confirmar nueva contraseña",
        validators=[
            Optional(),
            EqualTo("new_password", message="Las contraseñas no coinciden."),
        ],
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa un nombre válido.")

    def validate_telefono(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)
            digitos = "".join(char for char in field.data if char.isdigit())
            if len(digitos) < 10 or len(digitos) > 15:
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")
                raise ValidationError("Ingresa un teléfono válido de 10 a 15 dígitos.")

    def validate_calle(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)
            if not _has_letters(field.data):
                raise ValidationError("Ingresa una calle válida.")

    def validate_numero(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)

    def validate_colonia(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)
            if not _has_letters(field.data):
                raise ValidationError("Ingresa una colonia válida.")

    def validate_ciudad(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)

    def validate_estado(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)

    def validate_pais(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)

    def validate_cp(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)

    def validate_current_password(self, field):
        field.data = (field.data or "").strip()
        if field.data and " " in field.data:
            raise ValidationError("La contraseña actual no debe contener espacios.")

    def validate_new_password(self, field):
        field.data = (field.data or "").strip()
        if field.data and " " in field.data:
            raise ValidationError("La nueva contraseña no debe contener espacios.")

    def validate_confirm_new_password(self, field):
        field.data = (field.data or "").strip()

    def validate(self, extra_validators=None):
        initial_validation = super().validate(extra_validators=extra_validators)
        if not initial_validation:
            return False

        current_password = (self.current_password.data or "").strip()
        new_password = (self.new_password.data or "").strip()
        confirm_new_password = (self.confirm_new_password.data or "").strip()

        quiere_cambiar_password = bool(
            current_password or new_password or confirm_new_password
        )

        if quiere_cambiar_password:
            if not current_password:
                self.current_password.errors.append("Ingresa tu contraseña actual.")
                return False
            if not new_password:
                self.new_password.errors.append("Ingresa una nueva contraseña.")
                return False
            if not confirm_new_password:
                self.confirm_new_password.errors.append("Confirma la nueva contraseña.")
                return False
            if current_password == new_password:
                self.new_password.errors.append(
                    "La nueva contraseña no puede ser igual a la actual."
                )
                return False

        return True


class CreateStaffForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=2, max=120, message="El nombre debe tener entre 2 y 120 caracteres."
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$",
                message="El nombre solo puede contener letras y espacios.",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo válido."),
            Length(max=120, message="El correo no puede exceder 120 caracteres."),
        ],
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(
                min=6,
                max=100,
                message="La contraseña debe tener entre 6 y 100 caracteres.",
            ),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d).+$",
                message="La contraseña debe contener al menos una letra y un número.",
            ),
        ],
    )
    rol = SelectField(
        "Rol",
        choices=[("EMPLEADO", "Empleado/Vendedor"), ("ADMIN", "Admin")],
        validators=[DataRequired(message="Selecciona un rol.")],
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)
        if not _has_letters(field.data):
            raise ValidationError("Ingresa un nombre válido.")

    def validate_email(self, field):
        field.data = _normalize_spaces(field.data).lower()

    def validate_password(self, field):
        field.data = (field.data or "").strip()
        if " " in field.data:
            raise ValidationError("La contraseña no debe contener espacios.")


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
        validators=[DataRequired(message="El rol es requerido")],
        choices=[],
    )
    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[DataRequired(message="El estado es requerido")],
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1,
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
    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(message="El teléfono es requerido"),
            Length(
                min=10,
                max=10,
                message="El teléfono debe tener 10 caracteres",
            ),
            Regexp(
                r"^\d+$",
                message="El teléfono solo puede contener números",
            ),
        ],
    )


class ProveedorForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(
                min=3, max=150, message="El nombre debe tener entre 3 y 150 caracteres"
            ),
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
    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[DataRequired(message="El estado es requerido")],
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1,
    )


class ProductoForm(FlaskForm):
    id_categoria_producto = SelectField(
        "Categoría",
        coerce=int,
        validators=[DataRequired(message="La categoría es requerida")],
        choices=[],
    )

    id_receta = SelectField(
        "Receta",
        coerce=int,
        validators=[DataRequired(message="La receta es requerida")],
        choices=[],
    )

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(
                min=3, max=120, message="El nombre debe tener entre 3 y 120 caracteres"
            ),
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

    imagen = FileField(
        "Imagen",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                message="Solo se permiten imágenes JPG, JPEG, PNG o WEBP",
            ),
        ],
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)

    def validate_descripcion(self, field):
        if field.data:
            field.data = _normalize_spaces(field.data)


# MATERIA PRIMA
class MateriaPrimaForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es requerido"),
            Length(
                min=3, max=120, message="El nombre debe tener entre 3 y 120 caracteres"
            ),
        ],
    )

    id_categoria_materia_prima = SelectField(
        "Categoría",
        coerce=int,
        validators=[DataRequired(message="La categoría es requerida")],
        choices=[],
    )

    id_unidad_medida = SelectField(
        "Unidad de Medida",
        coerce=int,
        validators=[DataRequired(message="La unidad de medida es requerida")],
        choices=[],
    )

    id_proveedor = SelectField(
        "Proveedor",
        coerce=int,
        validators=[DataRequired(message="El proveedor es requerido")],
        choices=[],
    )

    stock_actual = DecimalField(
        "Stock Actual",
        validators=[
            InputRequired(message="El stock actual es requerido"),
            NumberRange(min=0, message="El stock debe ser mayor o igual a 0"),
        ],
    )

    stock_minimo = DecimalField(
        "Stock Mínimo",
        validators=[
            InputRequired(message="El stock mínimo es requerido"),
            NumberRange(min=0, message="El stock mínimo debe ser mayor o igual a 0"),
        ],
    )

    costo_unit_prom = DecimalField(
        "Costo Unitario Promedio",
        validators=[
            InputRequired(message="El costo unitario es requerido"),
            NumberRange(min=0, message="El costo debe ser mayor o igual a 0"),
        ],
    )

    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[DataRequired(message="El estado es requerido")],
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1,
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)


# RECETAS
class RecetaForm(FlaskForm):
    nombre = StringField(
        "Nombre de la Receta",
        validators=[
            DataRequired(message="El nombre de la receta es requerido"),
            Length(
                min=3, max=150, message="El nombre debe tener entre 3 y 150 caracteres"
            ),
        ],
    )
    rendimiento = DecimalField(
        "Rendimiento",
        validators=[
            DataRequired(message="El rendimiento es requerido"),
            NumberRange(min=1, message="El rendimiento debe ser mayor o igual a 1"),
        ],
    )
    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[DataRequired(message="El estado es requerido")],
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1,
    )

    def validate_nombre(self, field):
        field.data = _normalize_spaces(field.data)


# PRODUCCIÓN
class ProduccionForm(FlaskForm):
    id_producto = SelectField(
        "Producto",
        coerce=int,
        validators=[DataRequired(message="El producto es requerido")],
        choices=[],
    )
    id_lote = SelectField(
        "Lote de producción",
        coerce=int,
        validators=[DataRequired(message="El lote es requerido")],
        choices=[],
    )
    estado = SelectField(
        "Estado",
        validators=[DataRequired(message="El estado es requerido")],
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("EN_PROCESO", "En proceso"),
            ("COMPLETADA", "Completada"),
            ("CANCELADA", "Cancelada"),
        ],
        default="PENDIENTE",
    )
    observaciones = TextAreaField(
        "Observaciones",
        validators=[
            Optional(),
            Length(
                max=255, message="Las observaciones no pueden exceder 255 caracteres."
            ),
        ],
    )


class CategoriaProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre de la categoría",
        validators=[
            DataRequired(message="El nombre de la categoría es requerido"),
            Length(
                min=2,
                max=60,
                message="El nombre debe tener entre 2 y 60 caracteres",
            ),
            Regexp(
                r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-]+$",
                message="Solo se permiten letras, números, espacios y guiones",
            ),
        ],
    )


class CategoriaMateriaPrimaForm(FlaskForm):
    nombre = StringField(
        "Nombre de la categoría",
        validators=[
            DataRequired(message="El nombre de la categoría es requerido"),
            Length(
                min=2,
                max=60,
                message="El nombre debe tener entre 2 y 60 caracteres",
            ),
        ],
    )

    activo = SelectField(
        "Estado",
        coerce=int,
        validators=[DataRequired(message="El estado es requerido")],
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1,
    )
