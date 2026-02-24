# CasaLeon
Proyecto Integrador IDGS801

# Casa León — Sistema Integral de Gestión para Marroquinería (IDGS801)

Plataforma web para la gestión operativa y comercial de una fábrica de marroquinería en León, Guanajuato.  
Integra dos entornos conectados:

- **Tienda (Cliente):** catálogo, registro/login, carrito/checkout simulado, historial de pedidos.
- **Backoffice (Staff):** panel de administración/empleado, ventas POS, pedidos, inventario, producción y reportes.

---

## Estado actual (avance)
✅ Base de datos MySQL en 3FN con inventario tipo Kardex + triggers.  
✅ Autenticación funcional con roles (**ADMIN / EMPLEADO / CLIENTE**) usando `auth_tokens` (cookie HttpOnly).  
✅ UI base con **Tailwind + Flowbite** (Home público, Login/Register, dashboards por rol).  
✅ Build automático de Tailwind al iniciar Flask (sin correr `npm run watch`).

🟡 Próximo:
- Módulo **Cliente**: catálogo real, producto detalle, carrito, checkout, pedidos.
- Módulo **Empleado**: ventas POS, gestión de pedidos, consulta inventario.
- Módulo **Admin**: usuarios staff, catálogos, recetas (BOM), compras, reportes, auditoría.

---

## Tecnologías
**Backend**
- Python + Flask
- Flask-WTF (CSRF / forms)
- SQLAlchemy
- MySQL 8 (pieles_avance)

**Frontend**
- Tailwind CSS
- Flowbite

**DB**
- MySQL (contabilidad dura: inventario, compras, ventas, producción, kardex)
- NoSQL (planeado): MongoDB para carrito/pedidos (documentos)

---

## Requisitos
- Python 3.11+ (recomendado)
- MySQL 8.x
- Node.js 18+ (solo para compilar Tailwind con `npx`)
- Git / GitHub Desktop
- Instalar dependencias Node (para Tailwind/Flowbite)
Esto es necesario para que npx @tailwindcss/cli exista y se genere static/css/output.css.
npm install
- acuerdense del... .\.env\Scripts\activate

