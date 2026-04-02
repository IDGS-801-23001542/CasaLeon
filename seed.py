from app import app
from models import db, CategoriaProducto, Producto


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
        "Pulseras"
    ]

    for nombre in categorias:
        existe = CategoriaProducto.query.filter_by(nombre=nombre).first()
        if not existe:
            db.session.add(CategoriaProducto(nombre=nombre))

    db.session.commit()
    print("✔ Categorías insertadas")


def seed_productos():
    data = [
        ("Carteras", "Cartera Clásica León", 699, 18, "img/Producto1.jfif"),
        ("Monederos", "Monedero Compacto", 349, 25, "img/Producto2.jpeg"),
        ("Tarjeteros", "Tarjetero Ejecutivo", 299, 30, "img/Producto2.jpeg"),
        ("Cinturones", "Cinturón Heritage", 549, 20, "img/Producto3.jpeg"),
        ("Bolsas tote", "Bolsa Tote Siena", 1299, 14, "img/Producto1.jfif"),
        ("Bolsos de mano", "Bolso de Mano Verona", 1199, 12, "img/Producto4.jpeg"),
        ("Mochilas", "Mochila Andanza", 1699, 10, "img/Producto5.jpeg"),
        ("Mariconeras", "Mariconera Urbana", 899, 16, "img/Producto4.jpeg"),
        ("Portafolios", "Portafolio Ejecutivo", 1899, 8, "img/Producto1.jfif"),
        ("Neceseres", "Neceser Voyage", 599, 22, "img/Producto5.jpeg"),
        ("Fundas laptop", "Funda Laptop 15", 999, 11, "img/Producto5.jpeg"),
        ("Porta pasaportes", "Porta Pasaporte Atlas", 399, 26, "img/Producto2.jpeg"),
        ("Estuches lentes", "Estuche Óptico Classic", 379, 24, "img/Producto4.jpeg"),
        ("Llaveros", "Llavero Artesanal", 149, 40, "img/Producto3.jpeg"),
        ("Pulseras", "Pulsera Trenzada León", 199, 35, "img/Producto3.jpeg"),
    ]

    for categoria_nombre, nombre, precio, stock, imagen in data:
        categoria = CategoriaProducto.query.filter_by(nombre=categoria_nombre).first()

        if not categoria:
            print(f"⚠ Categoría no encontrada: {categoria_nombre}")
            continue

        existe = Producto.query.filter_by(nombre=nombre).first()
        if existe:
            continue

        producto = Producto(
            id_categoria_producto=categoria.id_categoria_producto,
            nombre=nombre,
            descripcion="Producto de cuero premium Casa León.",
            precio_venta=precio,
            stock_actual=stock,
            costo_unit_prom=precio * 0.4,
            activo=1,
            imagen=imagen
        )

        db.session.add(producto)

    db.session.commit()
    print("✔ Productos insertados")


def run_seed():
    with app.app_context():
        print("🌱 Ejecutando seed...")
        seed_categorias()
        seed_productos()
        print("✅ Seed completado")


if __name__ == "__main__":
    run_seed()