# DoomerPOS v4.0 — Versión de Alto Potencial

**DoomerPOS v4.0** es un sistema POS universitario avanzado para restaurantes, cafeterías, comedores, food trucks y negocios de comida. La versión v4.0 mejora la estructura anterior con un enfoque más profesional: seguridad por roles, flujo POS más ordenado, control de mesas, cocina/KDS, caja con arqueo, inventario con alertas, compras, proveedores, reportes gerenciales y bitácora de acciones importantes.

> Nota histórica: el proyecto nació como GastroPOS 360 y luego cambió oficialmente a DoomerPOS. Desde esta versión, el nombre visible del sistema es **DoomerPOS v4.0**.

## Objetivo del sistema

Centralizar la operación diaria de un restaurante desde la toma del pedido hasta el cierre financiero del turno, dejando trazabilidad de usuarios, pedidos, pagos, inventario, caja, reportes y auditoría.

## Mejoras principales de v4.0

- Interfaz más moderna, responsive y profesional.
- Dashboard ejecutivo con ventas del día, pedidos activos, mesas, caja e inventario bajo.
- POS con historial, búsqueda, filtros, descuentos, cargos adicionales y pago mixto.
- Pedidos con estados: `pendiente`, `en cocina`, `listo`, `servido`, `pagado`, `cancelado`.
- Mesas con estados visuales: `libre`, `ocupada`, `reservada`, `limpieza`.
- Cocina/KDS con columnas por estado, prioridad y tiempo abierto.
- Caja con apertura de turno, movimientos, ingresos, egresos, arqueo y cierre.
- Inventario con stock mínimo, alertas, entradas, salidas, ajustes y mermas.
- Compras relacionadas con proveedores activos o inactivos.
- Reportes por fecha: ventas, métodos de pago, productos más vendidos, ventas por usuario, caja, compras, inventario y mermas.
- Ticket/factura simulada imprimible para fines académicos.
- Seguridad con contraseñas cifradas, sesiones seguras, CSRF básico, permisos por rol y protección de rutas.
- Bitácora para inicio de sesión, creación, edición, cancelaciones, cierres y acciones sensibles.
- Páginas de error 400, 403, 404 y 500.
- Datos demo más realistas.
- `schema.sql` generado desde SQLAlchemy.

## Tecnologías utilizadas

- Python 3
- Flask 3
- Flask-SQLAlchemy
- SQLite para entorno académico
- HTML5, Jinja2, CSS moderno y JavaScript básico
- Werkzeug Security para cifrado de contraseñas

## Estructura del proyecto

```text
doomerpos_v4/
├── app/
│   ├── models/        # Modelos SQLAlchemy por dominio
│   ├── routes/        # Blueprints y controladores por módulo
│   ├── services/      # Reglas de negocio reutilizables
│   ├── utils/         # Seguridad, validaciones y decoradores
│   ├── templates/     # Pantallas HTML/Jinja2
│   └── static/        # CSS y JavaScript
├── docs/
├── config.py
├── run.py
├── requirements.txt
├── schema.sql
└── README.md
```

## Módulos incluidos

1. Autenticación y sesiones.
2. Roles y permisos.
3. Dashboard ejecutivo.
4. POS y pedidos.
5. Plano de mesas.
6. Cocina/KDS.
7. Caja, movimientos y cierres.
8. Productos y menú.
9. Inventario, mermas y alertas.
10. Compras y proveedores.
11. Reportes gerenciales.
12. Auditoría y bitácora.

## Usuario demo principal

```text
Usuario: admin
Contraseña: admin123
```

Usuarios demo adicionales:

```text
Usuario: gerente   Contraseña: gerente123
Usuario: cajero    Contraseña: cajero123
Usuario: mesero    Contraseña: mesero123
Usuario: cocina    Contraseña: cocina123
Usuario: inventario Contraseña: inventario123
```

## Control de interfaz por roles

DoomerPOS genera el menu lateral desde los permisos del usuario activo. Cada rol ve solo las opciones necesarias para su trabajo y las rutas tambien estan protegidas en servidor con decoradores de permisos. Si un usuario escribe manualmente una URL no autorizada, el sistema responde con error 403 y muestra un mensaje de acceso denegado.

La matriz central esta en `app/utils/permissions.py`. Desde ahi se definen permisos, roles y opciones de menu, lo que facilita agregar nuevos roles sin duplicar reglas en las plantillas.

Roles demo principales:

```text
admin / admin123           -> Administrador: acceso completo.
cajero / cajero123         -> Cajero: POS, pedidos, caja y reportes basicos de caja.
mesero / mesero123         -> Mesero: POS, pedidos y mesas.
cocina / cocina123         -> Cocina: Cocina/KDS y actualizacion de estados.
inventario / inventario123 -> Inventario: inventario, mermas, compras, proveedores y alertas.
gerente / gerente123       -> Gerencia: dashboard, reportes, caja, inventario y estadisticas.
```

Permisos destacados:

```text
dashboard.ver
pos.operar
pedidos.ver
pedidos.cobrar
mesas.ver
mesas.gestionar
cocina.operar
caja.ver
caja.abrir
caja.mover
caja.cerrar
inventario.ver
inventario.gestionar
compras.gestionar
proveedores.gestionar
reportes.ver
reportes.caja
usuarios.gestionar
roles.gestionar
auditoria.ver
sistema.configurar
```

## Instalación en Ubuntu

Instala dependencias del sistema:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv unzip -y
```

Descomprime el proyecto:

```bash
unzip doomerpos_v4.zip
cd doomerpos_v4
```

Crea y activa el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala dependencias de Python:

```bash
pip install -r requirements.txt
```

Inicializa la base de datos con datos demo:

```bash
flask --app run init-db
```

Ejecuta el sistema:

```bash
flask --app run
```

Abre en el navegador:

```text
http://127.0.0.1:5000
```

Para verlo desde otro dispositivo en la misma red:

```bash
flask --app run --host=0.0.0.0
```

Consulta la IP local de Ubuntu:

```bash
ip a
```

## Comandos útiles

Reiniciar base de datos:

```bash
flask --app run init-db
```

Generar `schema.sql` desde modelos:

```bash
flask --app run schema
```

## Seguridad aplicada

- Contraseñas cifradas con Werkzeug `scrypt`.
- Bloqueo temporal por intentos fallidos.
- Cookies de sesión `HttpOnly` y `SameSite=Lax`.
- Expiración de sesión.
- Decoradores `login_required` y `require_permission`.
- Protección CSRF básica para formularios.
- Cabeceras HTTP básicas: `X-Content-Type-Options`, `X-Frame-Options` y `Referrer-Policy`.
- Bitácora con usuario, módulo, acción, IP y navegador.

## Nota académica y fiscal

DoomerPOS v4.0 es un proyecto universitario funcional para demostrar arquitectura, procesos y control interno de un sistema POS para restaurantes. No debe considerarse una solución fiscal lista para producción. La facturación fiscal, integración bancaria y cumplimiento tributario deben validarse con proveedor autorizado y contador según la normativa local.
