from decimal import Decimal
from werkzeug.security import generate_password_hash
from datetime import datetime

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
    Venta,
    VentaDetalle,
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

    VentaDetalle.query.delete()
    Venta.query.delete()

    PedidoDetalle.query.delete()
    Pedido.query.delete()

    MateriaPrima.query.delete()
    CategoriaMateriaPrima.query.delete()
    UnidadMedida.query.delete()

    AuditoriaLog.query.delete()

    AuthToken.query.delete()
    Cliente.query.delete()
    Usuario.query.delete()
    Rol.query.delete()

    Proveedor.query.delete()

    Producto.query.delete()
    CategoriaProducto.query.delete()

    Lote.query.delete()

    db.session.commit()
    print("✔ Datos anteriores eliminados")


def seed_categorias_materia_prima():
    categorias = [
        "Cuero",
        "Forro",
        "Herrajes",
        "Químicos",
        "Costura",
        "Refuerzo",
        "Empaque",
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
            nombre="Martín López Herrera",
            email="admin@casaleon.com",
            telefono="4771010101",
            password_hash=generate_password_hash("Admin123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Ana Sofía Ramírez",
            email="empleado@casaleon.com",
            telefono="4772020202",
            password_hash=generate_password_hash("Empleado123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Diego Fernández Cruz",
            email="ventas@casaleon.com",
            telefono="4773030303",
            password_hash=generate_password_hash("Ventas123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Luis Arturo Navarro",
            email="produccion@casaleon.com",
            telefono="4774040404",
            password_hash=generate_password_hash("Produccion123"),
            activo=1,
        ),
        Usuario(
            id_rol=empleado_rol.id_rol,
            nombre="Paola Jiménez Ortega",
            email="compras@casaleon.com",
            telefono="4775050505",
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
            nombre="Juan Carlos Gómez Torres",
            rfc="GOTJ900315KJ2",
            email="juan.gomez@correo.com",
            telefono="4776123456",
            calle="Av. Panorama",
            numero="145",
            colonia="Panorama",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37160",
            password_hash=generate_password_hash("Cliente123"),
            activo=1,
        ),
        Cliente(
            nombre="María Fernanda Ruiz Saldaña",
            rfc="RUSM920824PU4",
            email="maria.ruiz@correo.com",
            telefono="4776987412",
            calle="Blvd. Campestre",
            numero="2208",
            colonia="Jardines del Moral",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37160",
            password_hash=generate_password_hash("Cliente123"),
            activo=1,
        ),
        Cliente(
            nombre="Carlos Alberto Mendoza Vega",
            rfc="MEVC910112NB7",
            email="carlos.mendoza@correo.com",
            telefono="4423012298",
            calle="Av. Universidad",
            numero="812",
            colonia="Centro Sur",
            ciudad="Querétaro",
            estado="Querétaro",
            pais="México",
            cp="76090",
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
            nombre="Pieles y Acabados del Bajío",
            rfc="PAB190315QH1",
            email="ventas@pabajio.com",
            telefono="4777142201",
            calle="Blvd. Timoteo Lozano",
            numero="4210",
            colonia="Ciudad Industrial",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37490",
            activo=1,
        ),
        Proveedor(
            nombre="Herrajes Finos de León",
            rfc="HFL180928LJ3",
            email="contacto@herrajesfinosleon.com",
            telefono="4777138842",
            calle="Calle Delta",
            numero="152",
            colonia="Industrial Delta",
            ciudad="León",
            estado="Guanajuato",
            pais="México",
            cp="37545",
            activo=1,
        ),
        Proveedor(
            nombre="Textiles y Forros del Centro",
            rfc="TFC170611MT8",
            email="pedidos@forroscentro.com",
            telefono="3331457788",
            calle="Av. Colón",
            numero="1880",
            colonia="Del Fresno",
            ciudad="Guadalajara",
            estado="Jalisco",
            pais="México",
            cp="44900",
            activo=1,
        ),
        Proveedor(
            nombre="Suministros Químicos Industriales MX",
            rfc="SQI160902DA5",
            email="ventas@sqmexico.com",
            telefono="8183321109",
            calle="Av. Ruiz Cortines",
            numero="5400",
            colonia="Mitras Norte",
            ciudad="Monterrey",
            estado="Nuevo León",
            pais="México",
            cp="64320",
            activo=1,
        ),
        Proveedor(
            nombre="Empaques y Accesorios de Piel Occidente",
            rfc="EAP210430TR6",
            email="info@eapoccidente.com",
            telefono="3319274650",
            calle="Calzada Independencia",
            numero="3245",
            colonia="San Andrés",
            ciudad="Guadalajara",
            estado="Jalisco",
            pais="México",
            cp="44810",
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
        (
            "Carteras",
            "CL-CAR-001",
            "Cartera Bifold Clásica",
            Decimal("899.00"),
            Decimal("18.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/cartera_tfstrs.jpg",
        ),
        (
            "Monederos",
            "CL-MON-001",
            "Monedero Compacto con Cierre",
            Decimal("429.00"),
            Decimal("28.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/monedero_lcrize.jpg",
        ),
        (
            "Tarjeteros",
            "CL-TAR-001",
            "Tarjetero Ejecutivo Slim",
            Decimal("359.00"),
            Decimal("26.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/tarjetero_s2sdli.jpg",
        ),
        (
            "Cinturones",
            "CL-CIN-001",
            "Cinturón Casual de Piel",
            Decimal("649.00"),
            Decimal("20.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031772/cinturon_wt16ky.jpg",
        ),
        (
            "Bolsas tote",
            "CL-TOT-001",
            "Bolsa Tote Siena",
            Decimal("1699.00"),
            Decimal("11.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031380/bolsaTote_oy10p0.jpg",
        ),
        (
            "Bolsos de mano",
            "CL-BOL-001",
            "Bolso de Mano Verona",
            Decimal("1499.00"),
            Decimal("10.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031772/bolsoMano_hjkdkd.jpg",
        ),
        (
            "Mochilas",
            "CL-MOC-001",
            "Mochila Urbana de Piel",
            Decimal("2199.00"),
            Decimal("8.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/mochila_r8f2b2.jpg",
        ),
        (
            "Mariconeras",
            "CL-MAR-001",
            "Mariconera Crossbody",
            Decimal("1099.00"),
            Decimal("14.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/mariconera_uh5yja.jpg",
        ),
        (
            "Portafolios",
            "CL-POR-001",
            "Portafolio Ejecutivo Premium",
            Decimal("2699.00"),
            Decimal("6.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/portafolio_cav9al.jpg",
        ),
        (
            "Neceseres",
            "CL-NEC-001",
            "Neceser de Viaje",
            Decimal("649.00"),
            Decimal("22.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031767/neceser_ogn1ti.jpg",
        ),
        (
            "Fundas laptop",
            "CL-FUN-001",
            "Funda Laptop 15 Pulgadas",
            Decimal("1299.00"),
            Decimal("11.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/fundaLaptop_kys2db.jpg",
        ),
        (
            "Porta pasaportes",
            "CL-PAS-001",
            "Porta Pasaporte Atlas",
            Decimal("469.00"),
            Decimal("24.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/portaPasaporte_yfgmxa.jpg",
        ),
        (
            "Estuches lentes",
            "CL-EST-001",
            "Estuche para Lentes Soft Case",
            Decimal("399.00"),
            Decimal("22.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/estucheLentes_g2wsng.jpg",
        ),
        (
            "Llaveros",
            "CL-LLA-001",
            "Llavero de Piel Artesanal",
            Decimal("189.00"),
            Decimal("45.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031771/llavero_jawo3i.jpg",
        ),
        (
            "Pulseras",
            "CL-PUL-001",
            "Pulsera Trenzada de Piel",
            Decimal("249.00"),
            Decimal("34.00"),
            "https://res.cloudinary.com/dazwaorxw/image/upload/v1776031768/pulsera_euavph.jpg",
        ),
    ]

    for categoria_nombre, sku, nombre, precio, stock, imagen in data:
        categoria = CategoriaProducto.query.filter_by(nombre=categoria_nombre).first()

        producto = Producto(
            id_categoria_producto=categoria.id_categoria_producto,
            sku=sku,
            nombre=nombre,
            descripcion=f"{nombre} elaborada con materiales para marroquinería y acabado artesanal.",
            precio_venta=precio,
            stock_actual=stock,
            costo_unit_prom=(precio * Decimal("0.42")).quantize(Decimal("0.01")),
            activo=1,
            imagen=imagen,
        )
        db.session.add(producto)

    db.session.commit()
    print("✔ Productos insertados")


def seed_materias_primas():
    materias = [
        # nombre, categoria, unidad, proveedor, stock_actual, stock_minimo, costo_unit_prom, merma_pct
        (
            "Cuero vacuno liso color café",
            "Cuero",
            "dm2",
            "Pieles y Acabados del Bajío",
            Decimal("950.00"),
            Decimal("120.00"),
            Decimal("29.50"),
            Decimal("6.00"),
        ),
        (
            "Cuero vacuno liso color negro",
            "Cuero",
            "dm2",
            "Pieles y Acabados del Bajío",
            Decimal("1100.00"),
            Decimal("140.00"),
            Decimal("28.80"),
            Decimal("6.00"),
        ),
        (
            "Cuero vacuno graneado miel",
            "Cuero",
            "dm2",
            "Pieles y Acabados del Bajío",
            Decimal("700.00"),
            Decimal("100.00"),
            Decimal("31.20"),
            Decimal("6.00"),
        ),
        (
            "Forro textil poliéster beige",
            "Forro",
            "m",
            "Textiles y Forros del Centro",
            Decimal("180.00"),
            Decimal("25.00"),
            Decimal("42.00"),
            Decimal("2.00"),
        ),
        (
            "Forro textil poliéster negro",
            "Forro",
            "m",
            "Textiles y Forros del Centro",
            Decimal("220.00"),
            Decimal("30.00"),
            Decimal("42.00"),
            Decimal("2.00"),
        ),
        (
            "Microfibra gamuzada camel",
            "Forro",
            "m",
            "Textiles y Forros del Centro",
            Decimal("90.00"),
            Decimal("15.00"),
            Decimal("68.00"),
            Decimal("2.00"),
        ),
        (
            "Cierre metálico 20 cm níquel",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("350.00"),
            Decimal("60.00"),
            Decimal("8.50"),
            Decimal("0.00"),
        ),
        (
            "Cierre metálico 35 cm níquel",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("240.00"),
            Decimal("40.00"),
            Decimal("14.50"),
            Decimal("0.00"),
        ),
        (
            "Hebilla clásica para cinturón 40 mm",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("180.00"),
            Decimal("30.00"),
            Decimal("32.00"),
            Decimal("0.00"),
        ),
        (
            "Broche magnético 18 mm",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("420.00"),
            Decimal("80.00"),
            Decimal("6.80"),
            Decimal("0.00"),
        ),
        (
            "Argolla D 25 mm",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("300.00"),
            Decimal("50.00"),
            Decimal("4.20"),
            Decimal("0.00"),
        ),
        (
            "Remache doble cabeza 9 mm",
            "Herrajes",
            "pieza",
            "Herrajes Finos de León",
            Decimal("1000.00"),
            Decimal("200.00"),
            Decimal("1.20"),
            Decimal("0.00"),
        ),
        (
            "Pegamento para cuero base solvente",
            "Químicos",
            "litro",
            "Suministros Químicos Industriales MX",
            Decimal("55.00"),
            Decimal("8.00"),
            Decimal("118.00"),
            Decimal("3.00"),
        ),
        (
            "Tinta para canto color café",
            "Químicos",
            "litro",
            "Suministros Químicos Industriales MX",
            Decimal("18.00"),
            Decimal("3.00"),
            Decimal("165.00"),
            Decimal("2.00"),
        ),
        (
            "Hilo encerado café 0.8 mm",
            "Costura",
            "m",
            "Textiles y Forros del Centro",
            Decimal("8000.00"),
            Decimal("1200.00"),
            Decimal("0.55"),
            Decimal("0.00"),
        ),
        (
            "Hilo encerado negro 0.8 mm",
            "Costura",
            "m",
            "Textiles y Forros del Centro",
            Decimal("8200.00"),
            Decimal("1200.00"),
            Decimal("0.55"),
            Decimal("0.00"),
        ),
        (
            "Espuma laminada 3 mm",
            "Refuerzo",
            "m",
            "Textiles y Forros del Centro",
            Decimal("110.00"),
            Decimal("15.00"),
            Decimal("36.00"),
            Decimal("1.00"),
        ),
        (
            "Entretela rígida adhesiva",
            "Refuerzo",
            "m",
            "Textiles y Forros del Centro",
            Decimal("130.00"),
            Decimal("20.00"),
            Decimal("24.00"),
            Decimal("1.00"),
        ),
        (
            "Caja kraft mediana",
            "Empaque",
            "pieza",
            "Empaques y Accesorios de Piel Occidente",
            Decimal("250.00"),
            Decimal("50.00"),
            Decimal("11.50"),
            Decimal("0.00"),
        ),
        (
            "Bolsa cubrepolvo de tela",
            "Empaque",
            "pieza",
            "Empaques y Accesorios de Piel Occidente",
            Decimal("180.00"),
            Decimal("40.00"),
            Decimal("9.80"),
            Decimal("0.00"),
        ),
    ]

    for (
        nombre,
        categoria_nombre,
        unidad_nombre,
        proveedor_nombre,
        stock,
        minimo,
        costo,
        merma,
    ) in materias:
        categoria = CategoriaMateriaPrima.query.filter_by(
            nombre=categoria_nombre
        ).first()
        unidad = UnidadMedida.query.filter_by(nombre=unidad_nombre).first()
        proveedor = Proveedor.query.filter_by(nombre=proveedor_nombre).first()

        if not categoria:
            raise ValueError(f"No existe la categoría: {categoria_nombre}")

        if not unidad:
            raise ValueError(f"No existe la unidad de medida: {unidad_nombre}")

        if not proveedor:
            raise ValueError(f"No existe el proveedor: {proveedor_nombre}")

        db.session.add(
            MateriaPrima(
                nombre=nombre,
                id_categoria_materia_prima=categoria.id_categoria_materia_prima,
                id_unidad_medida=unidad.id_unidad_medida,
                id_proveedor=proveedor.id_proveedor,
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
            "Cartera Bifold Clásica",
            "Receta Cartera Bifold Clásica",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("18.00")),
                ("Forro textil poliéster beige", Decimal("0.12")),
                ("Pegamento para cuero base solvente", Decimal("0.02")),
                ("Hilo encerado café 0.8 mm", Decimal("5.00")),
                ("Tinta para canto color café", Decimal("0.01")),
            ],
        ),
        (
            "Monedero Compacto con Cierre",
            "Receta Monedero Compacto con Cierre",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("8.00")),
                ("Forro textil poliéster negro", Decimal("0.06")),
                ("Cierre metálico 20 cm níquel", Decimal("1.00")),
                ("Pegamento para cuero base solvente", Decimal("0.01")),
                ("Hilo encerado negro 0.8 mm", Decimal("3.00")),
            ],
        ),
        (
            "Tarjetero Ejecutivo Slim",
            "Receta Tarjetero Ejecutivo Slim",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("7.00")),
                ("Microfibra gamuzada camel", Decimal("0.04")),
                ("Pegamento para cuero base solvente", Decimal("0.01")),
                ("Hilo encerado negro 0.8 mm", Decimal("2.50")),
                ("Tinta para canto color café", Decimal("0.01")),
            ],
        ),
        (
            "Cinturón Casual de Piel",
            "Receta Cinturón Casual de Piel",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("22.00")),
                ("Hebilla clásica para cinturón 40 mm", Decimal("1.00")),
                ("Hilo encerado café 0.8 mm", Decimal("2.00")),
                ("Tinta para canto color café", Decimal("0.01")),
            ],
        ),
        (
            "Bolsa Tote Siena",
            "Receta Bolsa Tote Siena",
            Decimal("1.00"),
            [
                ("Cuero vacuno graneado miel", Decimal("42.00")),
                ("Forro textil poliéster beige", Decimal("0.45")),
                ("Cierre metálico 35 cm níquel", Decimal("1.00")),
                ("Argolla D 25 mm", Decimal("2.00")),
                ("Pegamento para cuero base solvente", Decimal("0.05")),
                ("Hilo encerado café 0.8 mm", Decimal("12.00")),
                ("Entretela rígida adhesiva", Decimal("0.20")),
            ],
        ),
        (
            "Bolso de Mano Verona",
            "Receta Bolso de Mano Verona",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("34.00")),
                ("Microfibra gamuzada camel", Decimal("0.35")),
                ("Cierre metálico 35 cm níquel", Decimal("1.00")),
                ("Broche magnético 18 mm", Decimal("1.00")),
                ("Pegamento para cuero base solvente", Decimal("0.04")),
                ("Hilo encerado café 0.8 mm", Decimal("9.00")),
                ("Entretela rígida adhesiva", Decimal("0.18")),
            ],
        ),
        (
            "Mochila Urbana de Piel",
            "Receta Mochila Urbana de Piel",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("58.00")),
                ("Forro textil poliéster negro", Decimal("0.75")),
                ("Cierre metálico 35 cm níquel", Decimal("2.00")),
                ("Broche magnético 18 mm", Decimal("2.00")),
                ("Argolla D 25 mm", Decimal("4.00")),
                ("Pegamento para cuero base solvente", Decimal("0.08")),
                ("Hilo encerado negro 0.8 mm", Decimal("18.00")),
                ("Espuma laminada 3 mm", Decimal("0.35")),
            ],
        ),
        (
            "Mariconera Crossbody",
            "Receta Mariconera Crossbody",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("24.00")),
                ("Forro textil poliéster negro", Decimal("0.18")),
                ("Cierre metálico 20 cm níquel", Decimal("2.00")),
                ("Argolla D 25 mm", Decimal("2.00")),
                ("Pegamento para cuero base solvente", Decimal("0.03")),
                ("Hilo encerado negro 0.8 mm", Decimal("7.00")),
            ],
        ),
        (
            "Portafolio Ejecutivo Premium",
            "Receta Portafolio Ejecutivo Premium",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("68.00")),
                ("Microfibra gamuzada camel", Decimal("0.80")),
                ("Cierre metálico 35 cm níquel", Decimal("2.00")),
                ("Broche magnético 18 mm", Decimal("2.00")),
                ("Argolla D 25 mm", Decimal("4.00")),
                ("Remache doble cabeza 9 mm", Decimal("6.00")),
                ("Pegamento para cuero base solvente", Decimal("0.10")),
                ("Hilo encerado café 0.8 mm", Decimal("20.00")),
                ("Espuma laminada 3 mm", Decimal("0.40")),
                ("Entretela rígida adhesiva", Decimal("0.30")),
            ],
        ),
        (
            "Neceser de Viaje",
            "Receta Neceser de Viaje",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("16.00")),
                ("Forro textil poliéster negro", Decimal("0.16")),
                ("Cierre metálico 20 cm níquel", Decimal("1.00")),
                ("Pegamento para cuero base solvente", Decimal("0.02")),
                ("Hilo encerado negro 0.8 mm", Decimal("4.00")),
            ],
        ),
        (
            "Funda Laptop 15 Pulgadas",
            "Receta Funda Laptop 15 Pulgadas",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("30.00")),
                ("Microfibra gamuzada camel", Decimal("0.40")),
                ("Cierre metálico 35 cm níquel", Decimal("2.00")),
                ("Pegamento para cuero base solvente", Decimal("0.04")),
                ("Hilo encerado negro 0.8 mm", Decimal("8.00")),
                ("Espuma laminada 3 mm", Decimal("0.45")),
            ],
        ),
        (
            "Porta Pasaporte Atlas",
            "Receta Porta Pasaporte Atlas",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("9.00")),
                ("Microfibra gamuzada camel", Decimal("0.05")),
                ("Pegamento para cuero base solvente", Decimal("0.01")),
                ("Hilo encerado café 0.8 mm", Decimal("2.00")),
                ("Tinta para canto color café", Decimal("0.01")),
            ],
        ),
        (
            "Estuche para Lentes Soft Case",
            "Receta Estuche para Lentes Soft Case",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("10.00")),
                ("Microfibra gamuzada camel", Decimal("0.08")),
                ("Broche magnético 18 mm", Decimal("1.00")),
                ("Pegamento para cuero base solvente", Decimal("0.01")),
                ("Hilo encerado negro 0.8 mm", Decimal("2.00")),
                ("Espuma laminada 3 mm", Decimal("0.05")),
            ],
        ),
        (
            "Llavero de Piel Artesanal",
            "Receta Llavero de Piel Artesanal",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color café", Decimal("1.50")),
                ("Remache doble cabeza 9 mm", Decimal("1.00")),
                ("Hilo encerado café 0.8 mm", Decimal("0.50")),
            ],
        ),
        (
            "Pulsera Trenzada de Piel",
            "Receta Pulsera Trenzada de Piel",
            Decimal("1.00"),
            [
                ("Cuero vacuno liso color negro", Decimal("2.50")),
                ("Broche magnético 18 mm", Decimal("1.00")),
                ("Hilo encerado negro 0.8 mm", Decimal("0.50")),
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


def seed_movimientos_materia_prima():
    proveedor_cuero = Proveedor.query.filter_by(
        nombre="Pieles y Acabados del Bajío"
    ).first()
    proveedor_herrajes = Proveedor.query.filter_by(
        nombre="Herrajes Finos de León"
    ).first()
    proveedor_quimicos = Proveedor.query.filter_by(
        nombre="Suministros Químicos Industriales MX"
    ).first()

    movimientos = [
        (
            "Cuero vacuno liso color café",
            proveedor_cuero.id_proveedor,
            "ENTRADA",
            Decimal("180.00"),
            "Compra inicial de cuero café",
        ),
        (
            "Cuero vacuno liso color negro",
            proveedor_cuero.id_proveedor,
            "ENTRADA",
            Decimal("220.00"),
            "Compra inicial de cuero negro",
        ),
        (
            "Forro textil poliéster beige",
            None,
            "ENTRADA",
            Decimal("40.00"),
            "Ingreso por ajuste de inventario",
        ),
        (
            "Cierre metálico 20 cm níquel",
            proveedor_herrajes.id_proveedor,
            "ENTRADA",
            Decimal("100.00"),
            "Compra de cierres 20 cm",
        ),
        (
            "Hebilla clásica para cinturón 40 mm",
            proveedor_herrajes.id_proveedor,
            "ENTRADA",
            Decimal("40.00"),
            "Compra de hebillas",
        ),
        (
            "Pegamento para cuero base solvente",
            proveedor_quimicos.id_proveedor,
            "ENTRADA",
            Decimal("10.00"),
            "Compra de adhesivo",
        ),
    ]

    for nombre_mp, id_proveedor, tipo, cantidad, motivo in movimientos:
        mp = MateriaPrima.query.filter_by(nombre=nombre_mp).first()

        db.session.add(
            MovimientoMateriaPrima(
                id_materia_prima=mp.id_materia_prima,
                id_proveedor=id_proveedor,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
            )
        )

    db.session.commit()
    print("✔ Movimientos de materia prima insertados")


def seed_lotes():
    lotes = [
        ("Lote pequeño (10 piezas)", 10),
        ("Lote básico (20 piezas)", 20),
        ("Lote medio (50 piezas)", 50),
        ("Lote grande (100 piezas)", 100),
        ("Lote producción (200 piezas)", 200),
    ]

    for nombre, cantidad in lotes:
        db.session.add(Lote(nombre=nombre, cantidad=cantidad, activo=1))

    db.session.commit()
    print("✔ Lotes insertados")


def seed_pedidos():
    cliente_1 = Cliente.query.filter_by(email="juan.gomez@correo.com").first()
    cliente_2 = Cliente.query.filter_by(email="maria.ruiz@correo.com").first()

    cartera = Producto.query.filter_by(nombre="Cartera Bifold Clásica").first()
    monedero = Producto.query.filter_by(nombre="Monedero Compacto con Cierre").first()
    tote = Producto.query.filter_by(nombre="Bolsa Tote Siena").first()
    llavero = Producto.query.filter_by(nombre="Llavero de Piel Artesanal").first()

    pedido_1 = Pedido(
        id_cliente=cliente_1.id_cliente,
        folio="PED20260401-0001",
        estado="Entregado",
        total=Decimal("1508.00"),
        nombre_envio=cliente_1.nombre,
        telefono_envio=cliente_1.telefono,
        calle_envio=cliente_1.calle,
        numero_envio=cliente_1.numero,
        colonia_envio=cliente_1.colonia,
        ciudad_envio=cliente_1.ciudad,
        estado_envio=cliente_1.estado,
        pais_envio=cliente_1.pais,
        cp_envio=cliente_1.cp,
        notas="Entregar por la tarde",
    )
    db.session.add(pedido_1)
    db.session.flush()

    detalles_1 = [
        PedidoDetalle(
            id_pedido=pedido_1.id_pedido,
            id_producto=cartera.id_producto,
            producto_nombre=cartera.nombre,
            precio_unitario=cartera.precio_venta,
            cantidad=1,
            subtotal=cartera.precio_venta,
        ),
        PedidoDetalle(
            id_pedido=pedido_1.id_pedido,
            id_producto=monedero.id_producto,
            producto_nombre=monedero.nombre,
            precio_unitario=monedero.precio_venta,
            cantidad=1,
            subtotal=monedero.precio_venta,
        ),
        PedidoDetalle(
            id_pedido=pedido_1.id_pedido,
            id_producto=llavero.id_producto,
            producto_nombre=llavero.nombre,
            precio_unitario=llavero.precio_venta,
            cantidad=1,
            subtotal=llavero.precio_venta,
        ),
    ]
    db.session.add_all(detalles_1)

    pedido_2 = Pedido(
        id_cliente=cliente_2.id_cliente,
        folio="PED20260402-0002",
        estado="Pendiente",
        total=Decimal("1699.00"),
        nombre_envio=cliente_2.nombre,
        telefono_envio=cliente_2.telefono,
        calle_envio=cliente_2.calle,
        numero_envio=cliente_2.numero,
        colonia_envio=cliente_2.colonia,
        ciudad_envio=cliente_2.ciudad,
        estado_envio=cliente_2.estado,
        pais_envio=cliente_2.pais,
        cp_envio=cliente_2.cp,
        notas="Tocar antes de entregar",
    )
    db.session.add(pedido_2)
    db.session.flush()

    detalles_2 = [
        PedidoDetalle(
            id_pedido=pedido_2.id_pedido,
            id_producto=tote.id_producto,
            producto_nombre=tote.nombre,
            precio_unitario=tote.precio_venta,
            cantidad=1,
            subtotal=tote.precio_venta,
        ),
    ]
    db.session.add_all(detalles_2)

    pedido_3 = Pedido(
        id_cliente=cliente_1.id_cliente,
        folio="PED20260411-0003",
        estado="Entregado",
        total=Decimal("1088.00"),
        nombre_envio=cliente_1.nombre,
        telefono_envio=cliente_1.telefono,
        calle_envio=cliente_1.calle,
        numero_envio=cliente_1.numero,
        colonia_envio=cliente_1.colonia,
        ciudad_envio=cliente_1.ciudad,
        estado_envio=cliente_1.estado,
        pais_envio=cliente_1.pais,
        cp_envio=cliente_1.cp,
        notas="Entrega en recepción",
        creado_en=datetime(2026, 4, 11, 14, 30),
    )
    db.session.add(pedido_3)
    db.session.flush()

    detalles_3 = [
        PedidoDetalle(
            id_pedido=pedido_3.id_pedido,
            id_producto=cartera.id_producto,
            producto_nombre=cartera.nombre,
            precio_unitario=cartera.precio_venta,
            cantidad=1,
            subtotal=cartera.precio_venta,
        ),
            PedidoDetalle(
            id_pedido=pedido_3.id_pedido,
            id_producto=llavero.id_producto,
            producto_nombre=llavero.nombre,
            precio_unitario=llavero.precio_venta,
            cantidad=1,
            subtotal=llavero.precio_venta,
        ),
    ]
    db.session.add_all(detalles_3)

    pedido_4 = Pedido(
        id_cliente=cliente_2.id_cliente,
        folio="PED20260412-0004",
        estado="Pendiente",
        total=Decimal("2128.00"),
        nombre_envio=cliente_2.nombre,
        telefono_envio=cliente_2.telefono,
        calle_envio=cliente_2.calle,
        numero_envio=cliente_2.numero,
        colonia_envio=cliente_2.colonia,
        ciudad_envio=cliente_2.ciudad,
        estado_envio=cliente_2.estado,
        pais_envio=cliente_2.pais,
        cp_envio=cliente_2.cp,
        notas="Cliente solicita llamada previa",
        creado_en=datetime(2026, 4, 12, 11, 15),
    )
    db.session.add(pedido_4)
    db.session.flush()

    detalles_4 = [
        PedidoDetalle(
            id_pedido=pedido_4.id_pedido,
            id_producto=tote.id_producto,
            producto_nombre=tote.nombre,
            precio_unitario=tote.precio_venta,
            cantidad=1,
            subtotal=tote.precio_venta,
        ),
        PedidoDetalle(
            id_pedido=pedido_4.id_pedido,
            id_producto=monedero.id_producto,
            producto_nombre=monedero.nombre,
            precio_unitario=monedero.precio_venta,
            cantidad=1,
            subtotal=monedero.precio_venta,
        ),
    ]
    db.session.add_all(detalles_4)

    db.session.commit()
    print("✔ Pedidos demo insertados")


def seed_auditoria():
    logs = [
        AuditoriaLog(
            modulo="Autenticación",
            accion="Inicio de sesión",
            detalle="Usuario administrador inició sesión exitosamente",
            severidad="INFO",
            actor_nombre="Martín López Herrera",
            actor_email="admin@casaleon.com",
            ip_addr="192.168.1.100",
        ),
        AuditoriaLog(
            modulo="Compras",
            accion="Orden de compra registrada",
            detalle="Se registró una compra de cuero vacuno liso color café",
            severidad="INFO",
            actor_nombre="Paola Jiménez Ortega",
            actor_email="compras@casaleon.com",
            ip_addr="192.168.1.105",
        ),
        AuditoriaLog(
            modulo="Ventas",
            accion="Venta procesada",
            detalle="Venta VEN20260401-0001 procesada correctamente",
            severidad="INFO",
            actor_nombre="Diego Fernández Cruz",
            actor_email="ventas@casaleon.com",
            ip_addr="192.168.1.108",
        ),
        AuditoriaLog(
            modulo="Usuarios",
            accion="Usuario creado",
            detalle="Nuevo usuario 'produccion@casaleon.com' creado",
            severidad="INFO",
            actor_nombre="Martín López Herrera",
            actor_email="admin@casaleon.com",
            ip_addr="192.168.1.100",
        ),
        AuditoriaLog(
            modulo="Inventario",
            accion="Materia prima actualizada",
            detalle="Se actualizó el stock del material 'Cierre metálico 20 cm níquel'",
            severidad="INFO",
            actor_nombre="Ana Sofía Ramírez",
            actor_email="empleado@casaleon.com",
            ip_addr="192.168.1.112",
        ),
        AuditoriaLog(
            modulo="Producción",
            accion="Receta recalculada",
            detalle="Se recalculó el costo estimado de la receta 'Receta Bolsa Tote Siena'",
            severidad="INFO",
            actor_nombre="Luis Arturo Navarro",
            actor_email="produccion@casaleon.com",
            ip_addr="192.168.1.110",
        ),
        AuditoriaLog(
            modulo="Autenticación",
            accion="Cambio de contraseña",
            detalle="Usuario actualizó su contraseña correctamente",
            severidad="INFO",
            actor_nombre="Diego Fernández Cruz",
            actor_email="ventas@casaleon.com",
            ip_addr="192.168.1.108",
        ),
        AuditoriaLog(
            modulo="Pedidos",
            accion="Pedido entregado",
            detalle="Pedido PED20260401-0001 marcado como entregado",
            severidad="INFO",
            actor_nombre="Sistema",
            actor_email="sistema@casaleon.com",
            ip_addr="192.168.1.1",
        ),
        AuditoriaLog(
            modulo="Usuarios",
            accion="Acceso denegado",
            detalle="Intento de acceso sin permisos suficientes",
            severidad="WARNING",
            actor_nombre="Invitado",
            actor_email="invitado@casaleon.com",
            ip_addr="192.168.1.200",
        ),
        AuditoriaLog(
            modulo="Sistema",
            accion="Backup completado",
            detalle="Respaldo automático completado correctamente",
            severidad="INFO",
            actor_nombre="Sistema",
            actor_email="sistema@casaleon.com",
            ip_addr="192.168.1.1",
        ),
        AuditoriaLog(
            modulo="Proveedores",
            accion="Proveedor actualizado",
            detalle="Se actualizó información de 'Herrajes Finos de León'",
            severidad="INFO",
            actor_nombre="Paola Jiménez Ortega",
            actor_email="compras@casaleon.com",
            ip_addr="192.168.1.105",
        ),
    ]

    db.session.add_all(logs)
    db.session.commit()
    print("✔ Auditoría demo insertada")


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
        seed_movimientos_materia_prima()
        seed_lotes()
        seed_pedidos()
        seed_auditoria()

        print("✅ Seed completado")


if __name__ == "__main__":
    run_seed()
