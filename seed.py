from decimal import Decimal
from werkzeug.security import generate_password_hash

from app import create_app
from models import (
    db,
    Rol,
    Usuario,
    Cliente,
    AuthToken,
    CategoriaProducto,
    Producto,
    Pedido,
    PedidoDetalle,
    Proveedor,
    MateriaPrima,
    MovimientoMateriaPrima,
    Receta,
    RecetaDetalle,
    AuditoriaLog,
    CategoriaMateriaPrima,
    UnidadMedida,
    OrdenProduccion,
    OrdenProduccionDetalle,
    Merma,
    MermaDetalle,
    Lote,
)


def reset_data():
    print("🧹 Reiniciando datos...")

    MermaDetalle.query.delete()
    Merma.query.delete()

    OrdenProduccionDetalle.query.delete()
    OrdenProduccion.query.delete()

    RecetaDetalle.query.delete()
    Receta.query.delete()

    MovimientoMateriaPrima.query.delete()

    MateriaPrima.query.delete()
    CategoriaMateriaPrima.query.delete()
    UnidadMedida.query.delete()

    AuditoriaLog.query.delete()

    PedidoDetalle.query.delete()
    Pedido.query.delete()

    AuthToken.query.delete()
    Cliente.query.delete()
    Usuario.query.delete()
    Rol.query.delete()

    Proveedor.query.delete()

    Producto.query.delete()
    CategoriaProducto.query.delete()

    db.session.commit()
    print("✔ Datos anteriores eliminados")


def seed_categorias_materia_prima():
    categorias = [
        "Cuero",
        "Forro",
        "Herrajes",
        "Químicos",
        "Costura",
        "Relleno",
    ]

    for nombre in categorias:
        db.session.add(CategoriaMateriaPrima(nombre=nombre, activo=1))

    db.session.commit()
    print("✔ Categorías de materia prima insertadas")


def seed_unidades_medida():
    unidades = [
        "dm2",
        "m",
        "pieza",
        "litro",
    ]

    for nombre in unidades:
        db.session.add(UnidadMedida(nombre=nombre, activo=1))

    db.session.commit()
    print("✔ Unidades de medida insertadas")


def seed_roles():
    roles = [
        ("ADMIN", "Administrador"),
        ("EMPLEADO", "Empleado"),
    ]

    for codigo, descripcion in roles:
        db.session.add(Rol(codigo=codigo, descripcion=descripcion))

    db.session.commit()
    print("✔ Roles insertados")


def seed_staff():
    admin_rol = Rol.query.filter_by(codigo="ADMIN").first()
    empleado_rol = Rol.query.filter_by(codigo="EMPLEADO").first()

    usuarios = [
        Usuario(
            id_rol=admin_rol.id_rol,
            nombre="Administrador Casa León",
            email="admin@casaleon.com",
            password_hash=generate_password_hash("Admin123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Empleado Casa León",
            email="empleado@casaleon.com",
            password_hash=generate_password_hash("Empleado123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Ventas Casa León",
            email="ventas@casaleon.com",
            password_hash=generate_password_hash("Ventas123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Producción Casa León",
            email="produccion@casaleon.com",
            password_hash=generate_password_hash("Produccion123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Compras Casa León",
            email="compras@casaleon.com",
            password_hash=generate_password_hash("Compras123"),
            activo=1,
        ),
    ]

    db.session.add_all(usuarios)
    db.session.commit()
    print("✔ Staff insertado")


def seed_clientes():
    clientes = [
        Cliente(
            nombre="Juan Cliente",
            email="cliente1@correo.com",
            telefono="4771234567",
            calle="Av. Roma",
            numero="101",
            colonia="Centro",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37000",
            password_hash=generate_password_hash("Cliente123"),
            activo=1,
        ),
        Cliente(
            nombre="María Compradora",
            email="cliente2@correo.com",
            telefono="4779876543",
            calle="Blvd. Delta",
            numero="220",
            colonia="San Isidro",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37200",
            password_hash=generate_password_hash("Cliente123"),
            activo=1,
        ),
    ]

    db.session.add_all(clientes)
    db.session.commit()
    print("✔ Clientes insertados")


def seed_proveedores():
    proveedores = [
        Proveedor(
            nombre="Curtidos del Bajío",
            rfc="CUBA900101AAA",
            email="ventas@curtidosbajio.com",
            telefono="4771112233",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            activo=1,
        ),
        Proveedor(
            nombre="Herrajes León",
            rfc="HELE900101BBB",
            email="contacto@herrajesleon.com",
            telefono="4772223344",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            activo=1,
        ),
        Proveedor(
            nombre="Pegamentos Industriales MX",
            rfc="PEIM900101CCC",
            email="ventas@pegamentosmx.com",
            telefono="4773334455",
            ciudad="Guadalajara",
            estado="Jalisco",
            pais="México",
            activo=1,
        ),
        Proveedor(
            nombre="Textiles y Forros del Norte",
            rfc="TEFN900101DDD",
            email="compras@forrosnorte.com",
            telefono="8185556677",
            ciudad="Monterrey",
            estado="Nuevo León",
            pais="México",
            activo=1,
        ),
    ]

    db.session.add_all(proveedores)
    db.session.commit()
    print("✔ Proveedores insertados")


def seed_categorias():
    categorias = [
        "Carteras",
        "Monederos",
        "Tarjeteros",
        "Cinturones",
        "Bolsas tote",
        "Bolsos de mano",
        "Mochilas",
        "Mariconeras",
        "Portafolios",
        "Neceseres",
        "Fundas laptop",
        "Porta pasaportes",
        "Estuches lentes",
        "Llaveros",
        "Pulseras",
    ]

    for nombre in categorias:
        db.session.add(CategoriaProducto(nombre=nombre))

    db.session.commit()
    print("✔ Categorías insertadas")


def seed_productos():
    data = [
        ("Carteras", "CL-CAR-001", "Cartera Clásica León", 699, 18, "img/Producto1.jfif"),
        ("Monederos", "CL-MON-001", "Monedero Compacto", 349, 25, "img/Producto2.jpeg"),
        ("Tarjeteros", "CL-TAR-001", "Tarjetero Ejecutivo", 299, 30, "img/Producto2.jpeg"),
        ("Cinturones", "CL-CIN-001", "Cinturón Heritage", 549, 20, "img/Producto3.jpeg"),
        ("Bolsas tote", "CL-TOT-001", "Bolsa Tote Siena", 1299, 14, "img/Producto1.jfif"),
        ("Bolsos de mano", "CL-BOL-001", "Bolso de Mano Verona", 1199, 12, "img/Producto4.jpeg"),
        ("Mochilas", "CL-MOC-001", "Mochila Andanza", 1699, 10, "img/Producto5.jpeg"),
        ("Mariconeras", "CL-MAR-001", "Mariconera Urbana", 899, 16, "img/Producto4.jpeg"),
        ("Portafolios", "CL-POR-001", "Portafolio Ejecutivo", 1899, 8, "img/Producto1.jfif"),
        ("Neceseres", "CL-NEC-001", "Neceser Voyage", 599, 22, "img/Producto5.jpeg"),
        ("Fundas laptop", "CL-FUN-001", "Funda Laptop 15", 999, 11, "img/Producto5.jpeg"),
        ("Porta pasaportes", "CL-PAS-001", "Porta Pasaporte Atlas", 399, 26, "img/Producto2.jpeg"),
        ("Estuches lentes", "CL-EST-001", "Estuche Óptico Classic", 379, 24, "img/Producto4.jpeg"),
        ("Llaveros", "CL-LLA-001", "Llavero Artesanal", 149, 40, "img/Producto3.jpeg"),
        ("Pulseras", "CL-PUL-001", "Pulsera Trenzada León", 199, 35, "img/Producto3.jpeg"),
    ]

    for categoria_nombre, sku, nombre, precio, stock, imagen in data:
        categoria = CategoriaProducto.query.filter_by(nombre=categoria_nombre).first()

        producto = Producto(
            id_categoria_producto=categoria.id_categoria_producto,
            sku=sku,
            nombre=nombre,
            descripcion="Producto de cuero premium Casa León.",
            precio_venta=precio,
            stock_actual=stock,
            costo_unit_prom=round(precio * 0.4, 2),
            activo=1,
            imagen=imagen,
        )
        db.session.add(producto)

    db.session.commit()
    print("✔ Productos insertados")


def seed_materias_primas():
    materias = [
        ("Cuero vacuno premium café", "Cuero", "dm2", Decimal("850.00"), Decimal("100.00"), Decimal("28.00"), Decimal("5.00")),
        ("Cuero vacuno negro", "Cuero", "dm2", Decimal("700.00"), Decimal("100.00"), Decimal("26.50"), Decimal("5.00")),

        ("Forro textil beige", "Forro", "m", Decimal("150.00"), Decimal("20.00"), Decimal("45.00"), Decimal("2.00")),
        ("Forro textil negro", "Forro", "m", Decimal("120.00"), Decimal("20.00"), Decimal("45.00"), Decimal("2.00")),

        ("Cierre metálico 20cm", "Herrajes", "pieza", Decimal("320.00"), Decimal("50.00"), Decimal("18.00"), Decimal("0.00")),
        ("Cierre metálico 35cm", "Herrajes", "pieza", Decimal("240.00"), Decimal("40.00"), Decimal("22.00"), Decimal("0.00")),
        ("Hebilla cinturón clásica", "Herrajes", "pieza", Decimal("110.00"), Decimal("20.00"), Decimal("35.00"), Decimal("0.00")),
        ("Broche magnético", "Herrajes", "pieza", Decimal("180.00"), Decimal("30.00"), Decimal("12.00"), Decimal("0.00")),
        ("Remache decorativo", "Herrajes", "pieza", Decimal("500.00"), Decimal("100.00"), Decimal("2.50"), Decimal("0.00")),

        ("Pegamento industrial", "Químicos", "litro", Decimal("40.00"), Decimal("5.00"), Decimal("90.00"), Decimal("3.00")),

        ("Hilo encerado café", "Costura", "m", Decimal("6000.00"), Decimal("1000.00"), Decimal("0.06"), Decimal("0.00")),
        ("Hilo encerado negro", "Costura", "m", Decimal("6000.00"), Decimal("1000.00"), Decimal("0.06"), Decimal("0.00")),

        ("Espuma de protección", "Relleno", "m", Decimal("80.00"), Decimal("10.00"), Decimal("30.00"), Decimal("1.00")),
    ]

    for nombre, categoria_nombre, unidad_nombre, stock, minimo, costo, merma in materias:
        categoria = CategoriaMateriaPrima.query.filter_by(nombre=categoria_nombre).first()
        unidad = UnidadMedida.query.filter_by(nombre=unidad_nombre).first()

        db.session.add(
            MateriaPrima(
                nombre=nombre,
                id_categoria_materia_prima=categoria.id_categoria_materia_prima,
                id_unidad_medida=unidad.id_unidad_medida,
                stock_actual=stock,
                stock_minimo=minimo,
                costo_unit_prom=costo,
                merma_pct=merma,
                activo=1,
            )
        )

    db.session.commit()
    print("✔ Materias primas insertadas")


def costo_receta(detalles):
    total = Decimal("0")

    for nombre_mp, cantidad in detalles:
        mp = MateriaPrima.query.filter_by(nombre=nombre_mp).first()
        costo = Decimal(str(mp.costo_unit_prom or 0))
        merma_pct = Decimal(str(mp.merma_pct or 0))
        cantidad_base = Decimal(str(cantidad))
        cantidad_real = cantidad_base * (Decimal("1") + (merma_pct / Decimal("100")))
        total += costo * cantidad_real

    return total.quantize(Decimal("0.01"))


def seed_recetas():
    recetas_data = [
        (
            "Cartera Clásica León",
            "Receta Cartera Clásica León",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("35.00")),
                ("Forro textil beige", Decimal("0.20")),
                ("Cierre metálico 20cm", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.05")),
                ("Hilo encerado café", Decimal("10.00")),
            ],
        ),
        (
            "Monedero Compacto",
            "Receta Monedero Compacto",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("12.00")),
                ("Forro textil negro", Decimal("0.08")),
                ("Cierre metálico 20cm", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.02")),
                ("Hilo encerado negro", Decimal("5.00")),
            ],
        ),
        (
            "Tarjetero Ejecutivo",
            "Receta Tarjetero Ejecutivo",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("10.00")),
                ("Forro textil negro", Decimal("0.04")),
                ("Pegamento industrial", Decimal("0.01")),
                ("Hilo encerado negro", Decimal("3.00")),
            ],
        ),
        (
            "Cinturón Heritage",
            "Receta Cinturón Heritage",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("45.00")),
                ("Hebilla cinturón clásica", Decimal("1.00")),
                ("Hilo encerado café", Decimal("6.00")),
            ],
        ),
        (
            "Bolsa Tote Siena",
            "Receta Bolsa Tote Siena",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("90.00")),
                ("Forro textil beige", Decimal("0.45")),
                ("Cierre metálico 35cm", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.08")),
                ("Hilo encerado café", Decimal("16.00")),
                ("Espuma de protección", Decimal("0.25")),
            ],
        ),
        (
            "Bolso de Mano Verona",
            "Receta Bolso de Mano Verona",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("75.00")),
                ("Forro textil beige", Decimal("0.40")),
                ("Cierre metálico 35cm", Decimal("1.00")),
                ("Broche magnético", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.08")),
                ("Hilo encerado café", Decimal("15.00")),
                ("Espuma de protección", Decimal("0.20")),
            ],
        ),
        (
            "Mochila Andanza",
            "Receta Mochila Andanza",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("120.00")),
                ("Forro textil negro", Decimal("0.80")),
                ("Cierre metálico 35cm", Decimal("3.00")),
                ("Broche magnético", Decimal("2.00")),
                ("Pegamento industrial", Decimal("0.12")),
                ("Hilo encerado negro", Decimal("25.00")),
                ("Espuma de protección", Decimal("0.35")),
            ],
        ),
        (
            "Mariconera Urbana",
            "Receta Mariconera Urbana",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("50.00")),
                ("Forro textil negro", Decimal("0.25")),
                ("Cierre metálico 20cm", Decimal("2.00")),
                ("Pegamento industrial", Decimal("0.05")),
                ("Hilo encerado negro", Decimal("10.00")),
                ("Broche magnético", Decimal("1.00")),
            ],
        ),
        (
            "Portafolio Ejecutivo",
            "Receta Portafolio Ejecutivo",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("140.00")),
                ("Forro textil beige", Decimal("0.90")),
                ("Cierre metálico 35cm", Decimal("2.00")),
                ("Broche magnético", Decimal("2.00")),
                ("Pegamento industrial", Decimal("0.15")),
                ("Hilo encerado café", Decimal("30.00")),
                ("Espuma de protección", Decimal("0.40")),
                ("Remache decorativo", Decimal("6.00")),
            ],
        ),
        (
            "Neceser Voyage",
            "Receta Neceser Voyage",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("30.00")),
                ("Forro textil negro", Decimal("0.20")),
                ("Cierre metálico 20cm", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.03")),
                ("Hilo encerado negro", Decimal("6.00")),
            ],
        ),
        (
            "Funda Laptop 15",
            "Receta Funda Laptop 15",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("80.00")),
                ("Forro textil negro", Decimal("0.50")),
                ("Cierre metálico 35cm", Decimal("2.00")),
                ("Pegamento industrial", Decimal("0.08")),
                ("Hilo encerado negro", Decimal("12.00")),
                ("Espuma de protección", Decimal("0.50")),
            ],
        ),
        (
            "Porta Pasaporte Atlas",
            "Receta Porta Pasaporte Atlas",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("18.00")),
                ("Forro textil beige", Decimal("0.08")),
                ("Pegamento industrial", Decimal("0.02")),
                ("Hilo encerado café", Decimal("4.00")),
            ],
        ),
        (
            "Estuche Óptico Classic",
            "Receta Estuche Óptico Classic",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("20.00")),
                ("Forro textil negro", Decimal("0.10")),
                ("Broche magnético", Decimal("1.00")),
                ("Pegamento industrial", Decimal("0.02")),
                ("Hilo encerado negro", Decimal("4.00")),
                ("Espuma de protección", Decimal("0.05")),
            ],
        ),
        (
            "Llavero Artesanal",
            "Receta Llavero Artesanal",
            Decimal("1.00"),
            [
                ("Cuero vacuno premium café", Decimal("3.00")),
                ("Remache decorativo", Decimal("1.00")),
                ("Hilo encerado café", Decimal("1.00")),
            ],
        ),
        (
            "Pulsera Trenzada León",
            "Receta Pulsera Trenzada León",
            Decimal("1.00"),
            [
                ("Cuero vacuno negro", Decimal("5.00")),
                ("Broche magnético", Decimal("1.00")),
                ("Hilo encerado negro", Decimal("1.00")),
            ],
        ),
    ]

    for producto_nombre, nombre_receta, rendimiento, detalles in recetas_data:
        producto = Producto.query.filter_by(nombre=producto_nombre).first()

        receta = Receta(
            id_producto=producto.id_producto,
            nombre=nombre_receta,
            rendimiento=rendimiento,
            costo_estimado=costo_receta(detalles),
            activo=1,
        )
        db.session.add(receta)
        db.session.flush()

        for nombre_mp, cantidad in detalles:
            mp = MateriaPrima.query.filter_by(nombre=nombre_mp).first()
            db.session.add(
                RecetaDetalle(
                    id_receta=receta.id_receta,
                    id_materia_prima=mp.id_materia_prima,
                    cantidad=cantidad,
                )
            )

    db.session.commit()
    print("✔ Recetas insertadas")


def seed_pedidos():
    cliente = Cliente.query.filter_by(email="cliente1@correo.com").first()
    producto1 = Producto.query.filter_by(nombre="Cartera Clásica León").first()
    producto2 = Producto.query.filter_by(nombre="Monedero Compacto").first()

    pedido = Pedido(
        id_cliente=cliente.id_cliente,
        folio="PED20260401-0001",
        estado="Pendiente",
        total=Decimal("1048.00"),
        nombre_envio=cliente.nombre,
        telefono_envio=cliente.telefono,
        calle_envio=cliente.calle,
        numero_envio=cliente.numero,
        colonia_envio=cliente.colonia,
        ciudad_envio=cliente.ciudad,
        estado_envio=cliente.estado,
        pais_envio=cliente.pais,
        cp_envio=cliente.cp,
        notas="Entregar por la tarde",
    )
    db.session.add(pedido)
    db.session.flush()

    detalles = [
        PedidoDetalle(
            id_pedido=pedido.id_pedido,
            id_producto=producto1.id_producto,
            producto_nombre=producto1.nombre,
            precio_unitario=producto1.precio_venta,
            cantidad=1,
            subtotal=producto1.precio_venta,
        ),
        PedidoDetalle(
            id_pedido=pedido.id_pedido,
            id_producto=producto2.id_producto,
            producto_nombre=producto2.nombre,
            precio_unitario=producto2.precio_venta,
            cantidad=1,
            subtotal=producto2.precio_venta,
        ),
    ]

    db.session.add_all(detalles)
    db.session.commit()
    print("✔ Pedidos demo insertados")


def seed_auditoria():
    logs = [
        AuditoriaLog(modulo="Autenticación", accion="Inicio de sesión", detalle="Usuario administrador inició sesión exitosamente", severidad="INFO", actor_nombre="Administrador Casa León", actor_email="admin@casaleon.com", ip_addr="192.168.1.100"),
        AuditoriaLog(modulo="Compras", accion="Orden de compra creada", detalle="Nueva orden OC-2026-045 creada", severidad="INFO", actor_nombre="Compras Casa León", actor_email="compras@casaleon.com", ip_addr="192.168.1.105"),
        AuditoriaLog(modulo="Ventas", accion="Error de validación", detalle="Intento de venta con stock insuficiente", severidad="WARNING", actor_nombre="Ventas Casa León", actor_email="ventas@casaleon.com", ip_addr="192.168.1.108"),
        AuditoriaLog(modulo="Usuarios", accion="Usuario creado", detalle="Nuevo usuario 'produccion@casaleon.com' creado", severidad="INFO", actor_nombre="Administrador Casa León", actor_email="admin@casaleon.com", ip_addr="192.168.1.100"),
        AuditoriaLog(modulo="Inventario", accion="Inventario actualizado", detalle="Stock del producto CL-CAR-001 actualizado", severidad="INFO", actor_nombre="Empleado Casa León", actor_email="empleado@casaleon.com", ip_addr="192.168.1.112"),
        AuditoriaLog(modulo="Pagos", accion="Error de conexión", detalle="Timeout con proveedor de pagos", severidad="ERROR", actor_nombre="Sistema", actor_email="sistema@casaleon.com", ip_addr="192.168.1.1"),
        AuditoriaLog(modulo="Autenticación", accion="Cambio de contraseña", detalle="Usuario cambió su contraseña exitosamente", severidad="INFO", actor_nombre="Ventas Casa León", actor_email="ventas@casaleon.com", ip_addr="192.168.1.108"),
        AuditoriaLog(modulo="Producción", accion="Orden de producción completada", detalle="Orden OP-2026-123 completada", severidad="INFO", actor_nombre="Producción Casa León", actor_email="produccion@casaleon.com", ip_addr="192.168.1.110"),
        AuditoriaLog(modulo="Autenticación", accion="Acceso denegado", detalle="Intento de acceso sin permisos suficientes", severidad="WARNING", actor_nombre="Invitado", actor_email="invitado@casaleon.com", ip_addr="192.168.1.200"),
        AuditoriaLog(modulo="Sistema", accion="Backup completado", detalle="Respaldo automático completado", severidad="INFO", actor_nombre="Sistema", actor_email="sistema@casaleon.com", ip_addr="192.168.1.1"),
        AuditoriaLog(modulo="Usuarios", accion="Permisos modificados", detalle="Permisos de usuario 'ventas@casaleon.com' actualizados", severidad="WARNING", actor_nombre="Administrador Casa León", actor_email="admin@casaleon.com", ip_addr="192.168.1.100"),
        AuditoriaLog(modulo="Ventas", accion="Venta procesada", detalle="Venta VEN-2026-892 procesada exitosamente", severidad="INFO", actor_nombre="Ventas Casa León", actor_email="ventas@casaleon.com", ip_addr="192.168.1.108"),
        AuditoriaLog(modulo="Sistema", accion="Error crítico", detalle="Espacio en disco por debajo del 10%", severidad="CRITICAL", actor_nombre="Sistema", actor_email="sistema@casaleon.com", ip_addr="192.168.1.1"),
        AuditoriaLog(modulo="Usuarios", accion="Usuario eliminado", detalle="Usuario temporal eliminado del sistema", severidad="WARNING", actor_nombre="Administrador Casa León", actor_email="admin@casaleon.com", ip_addr="192.168.1.100"),
        AuditoriaLog(modulo="Proveedores", accion="Proveedor actualizado", detalle="Información de proveedor PROV-015 actualizada", severidad="INFO", actor_nombre="Compras Casa León", actor_email="compras@casaleon.com", ip_addr="192.168.1.105"),
    ]

    db.session.add_all(logs)
    db.session.commit()
    print("✔ Auditoría demo insertada")


def seed_lotes():
    lotes = [
        ("Lote pequeño (10 piezas)", 10),
        ("Lote básico (20 piezas)", 20),
        ("Lote medio (50 piezas)", 50),
        ("Lote grande (100 piezas)", 100),
        ("Lote producción (200 piezas)", 200),
    ]

    for nombre, cantidad in lotes:
        db.session.add(
            Lote(
                nombre=nombre,
                cantidad=cantidad,
                activo=1
            )
        )

    db.session.commit()
    print("✔ Lotes insertados")


def run_seed():
    app = create_app()
    with app.app_context():
        print("Ejecutando seed...")

        db.drop_all()
        db.create_all()

        seed_roles()
        seed_staff()
        seed_clientes()
        seed_proveedores()
        seed_categorias()
        seed_productos()
        seed_categorias_materia_prima()
        seed_unidades_medida()
        seed_materias_primas()
        seed_recetas()
        seed_pedidos()
        seed_auditoria()
        seed_lotes()

        print("✅ Seed completado")


if __name__ == "__main__":
    run_seed()