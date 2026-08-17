from decimal import Decimal
from datetime import datetime, timedelta
from flask import Flask, render_template, session, request, abort
from sqlalchemy import text
from app.extensions import db
from app.utils.security import cargar_usuario_actual
from app.utils.permissions import PERMISSION_LABELS, ROLE_PERMISSIONS
import secrets


def generar_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def proteger_csrf():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        token_sesion = session.get("_csrf_token")
        token_form = request.form.get("_csrf_token") or request.headers.get("X-CSRFToken")
        if not token_sesion or not token_form or token_sesion != token_form:
            abort(400)


def create_app(config_object="config.Config"):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    db.init_app(app)

    from app import models  # noqa: F401
    app.before_request(cargar_usuario_actual)
    app.before_request(proteger_csrf)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    @app.context_processor
    def inject_security_helpers():
        return {"csrf_token": generar_csrf_token()}

    from app.routes.auth_routes import bp as auth_bp
    from app.routes.dashboard_routes import bp as dashboard_bp
    from app.routes.pos_routes import bp as pos_bp
    from app.routes.mesas_routes import bp as mesas_bp
    from app.routes.cocina_routes import bp as cocina_bp
    from app.routes.caja_routes import bp as caja_bp
    from app.routes.inventario_routes import bp as inventario_bp
    from app.routes.compras_routes import bp as compras_bp
    from app.routes.reportes_routes import bp as reportes_bp
    from app.routes.usuarios_routes import bp as usuarios_bp
    from app.routes.auditoria_routes import bp as auditoria_bp
    from app.routes.productos_routes import bp as productos_bp

    for bp in [auth_bp, dashboard_bp, pos_bp, mesas_bp, cocina_bp, caja_bp, inventario_bp, compras_bp, reportes_bp, usuarios_bp, auditoria_bp, productos_bp]:
        app.register_blueprint(bp)

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        """Crea la base de datos e inserta datos demo de DoomerPOS v4.0."""
        inicializar_base_demo()
        print("Base de datos inicializada. Usuario demo: admin / admin123")

    @app.cli.command("schema")
    def schema_command():
        """Genera schema.sql desde los modelos actuales."""
        generar_schema_sql()
        print("schema.sql actualizado para DoomerPOS v4.0.")

    return app


def inicializar_base_demo():
    from app.models import (
        Almacen, CanalVenta, CategoriaProducto, Cliente, Reserva, Compra, DetalleCompra, DetallePedido,
        Impuesto, Inventario, Mesa, MetodoPago, MovimientoCaja, MovimientoInventario, Pago,
        Pedido, Permiso, Producto, Proveedor, Rol, Sucursal, Terminal, Turno, Usuario, CierreCaja,
    )
    from app.services.pedidos_service import recalcular_totales

    db.drop_all()
    db.create_all()

    permisos_data = sorted(PERMISSION_LABELS.items())
    permisos = {codigo: Permiso(codigo=codigo, descripcion=desc) for codigo, desc in permisos_data}
    db.session.add_all(permisos.values())

    def rol(nombre, descripcion, codigos):
        r = Rol(nombre=nombre, descripcion=descripcion)
        r.permisos = [permisos[c] for c in codigos]
        return r

    descripciones_roles = {
        "Administrador": "Acceso total al sistema",
        "Gerencia": "Consulta ejecutiva de dashboard, reportes, caja e inventario",
        "Gerente/Supervisor": "Alias demo de gerencia para compatibilidad",
        "Consulta": "Consulta operativa sin acciones de escritura",
        "Cajero": "Ventas, cobros y control de caja",
        "Mesero": "Atención de mesas y pedidos",
        "Cocina": "Preparación y actualización de comandas",
        "Cocina/Barra": "Alias demo de cocina para compatibilidad",
        "Inventario": "Stock, mermas, compras y proveedores",
        "Inventario/Almacén": "Alias demo de inventario para compatibilidad",
    }
    roles = {
        nombre: rol(nombre, descripciones_roles.get(nombre, "Rol operativo"), codigos)
        for nombre, codigos in ROLE_PERMISSIONS.items()
    }
    db.session.add_all(roles.values())

    sucursal = Sucursal(nombre="DoomerPOS Restaurante Central", direccion="Comayagua, Honduras", telefono="0000-0000")
    db.session.add(sucursal)
    db.session.flush()

    terminal = Terminal(id_sucursal=sucursal.id_sucursal, codigo_terminal="DPOS-01", tipo="Caja principal")
    almacen = Almacen(id_sucursal=sucursal.id_sucursal, nombre="Almacén principal", ubicacion="Bodega interna")
    mesas = [Mesa(id_sucursal=sucursal.id_sucursal, numero_mesa=str(i), zona="Salón", capacidad=4, estado="libre") for i in range(1, 9)]
    mesas.append(Mesa(id_sucursal=sucursal.id_sucursal, numero_mesa="T1", zona="Terraza", capacidad=6, estado="reservada"))
    canales = [CanalVenta(nombre=n, descripcion=f"Canal {n}") for n in ["Mesa", "Mostrador", "QR", "Kiosko", "Delivery", "Online"]]
    metodos = [MetodoPago(nombre=n, descripcion=f"Pago con {n}") for n in ["Efectivo", "Tarjeta", "Transferencia", "Mixto"]]
    impuesto = Impuesto(nombre="ISV", porcentaje=Decimal("15.00"))
    db.session.add_all([terminal, almacen, *mesas, *canales, *metodos, impuesto])
    db.session.flush()

    def crear_usuario(nombre, login, password, rol_nombre):
        u = Usuario(id_rol=roles[rol_nombre].id_rol, id_sucursal=sucursal.id_sucursal, nombre=nombre, usuario_login=login)
        u.set_password(password)
        return u

    usuarios = [
        crear_usuario("Administrador Demo", "admin", "admin123", "Administrador"),
        crear_usuario("Gerente Demo", "gerente", "gerente123", "Gerencia"),
        crear_usuario("Cajero Demo", "cajero", "cajero123", "Cajero"),
        crear_usuario("Mesero Demo", "mesero", "mesero123", "Mesero"),
        crear_usuario("Cocina Demo", "cocina", "cocina123", "Cocina"),
        crear_usuario("Inventario Demo", "inventario", "inventario123", "Inventario"),
    ]
    db.session.add_all(usuarios)
    db.session.flush()
    admin_user, gerente_user, cajero_user, mesero_user, cocina_user, inventario_user = usuarios

    categorias = [
        CategoriaProducto(nombre="Comidas", descripcion="Platos principales"),
        CategoriaProducto(nombre="Bebidas", descripcion="Bebidas frías y calientes"),
        CategoriaProducto(nombre="Postres", descripcion="Dulces y postres"),
    ]
    db.session.add_all(categorias)
    db.session.flush()

    productos = [
        Producto(id_categoria=categorias[0].id_categoria, codigo="COM-001", nombre="Hamburguesa clásica", precio=Decimal("145.00"), costo_estimado=Decimal("70.00"), stock_minimo=Decimal("8")),
        Producto(id_categoria=categorias[0].id_categoria, codigo="COM-002", nombre="Pizza personal", precio=Decimal("180.00"), costo_estimado=Decimal("85.00"), stock_minimo=Decimal("6")),
        Producto(id_categoria=categorias[0].id_categoria, codigo="COM-003", nombre="Alitas BBQ", precio=Decimal("165.00"), costo_estimado=Decimal("78.00"), stock_minimo=Decimal("7")),
        Producto(id_categoria=categorias[1].id_categoria, codigo="BEB-001", nombre="Refresco", precio=Decimal("35.00"), costo_estimado=Decimal("15.00"), stock_minimo=Decimal("12")),
        Producto(id_categoria=categorias[1].id_categoria, codigo="BEB-002", nombre="Café americano", precio=Decimal("45.00"), costo_estimado=Decimal("12.00"), stock_minimo=Decimal("10")),
        Producto(id_categoria=categorias[2].id_categoria, codigo="POS-001", nombre="Flan", precio=Decimal("60.00"), costo_estimado=Decimal("25.00"), stock_minimo=Decimal("5")),
    ]
    db.session.add_all(productos)
    db.session.flush()

    existencias = [35, 20, 4, 60, 40, 3]
    for producto, stock in zip(productos, existencias):
        inv = Inventario(id_almacen=almacen.id_almacen, id_producto=producto.id_producto, existencia_actual=Decimal(stock), costo_promedio=producto.costo_estimado)
        db.session.add(inv)
        db.session.add(MovimientoInventario(id_almacen=almacen.id_almacen, id_producto=producto.id_producto, id_usuario=admin_user.id_usuario, tipo="Entrada", cantidad=Decimal(stock), motivo="Carga inicial demo"))

    clientes = [Cliente(nombre="Cliente general"), Cliente(nombre="Ana Martínez", telefono="9999-0001", correo="ana@example.com"), Cliente(nombre="Carlos Rivera", telefono="9999-0002"), Cliente(nombre="Familia López", telefono="9999-0003", correo="lopez@example.com")]
    proveedor = Proveedor(nombre="Proveedor Demo S.A.", telefono="0000-1111", correo="ventas@proveedordemo.com", contacto="Ejecutivo Demo")
    db.session.add_all([*clientes, proveedor])
    db.session.flush()
    reserva = Reserva(id_cliente=clientes[3].id_cliente, id_mesa=mesas[-1].id_mesa, fecha_reserva=datetime.utcnow() + timedelta(hours=3), personas=5, estado="Confirmada", notas="Reserva demo para terraza")
    db.session.add(reserva)

    compra = Compra(id_proveedor=proveedor.id_proveedor, id_almacen=almacen.id_almacen, total_compra=Decimal("3200.00"), observacion="Compra demo inicial")
    db.session.add(compra)
    db.session.flush()
    db.session.add(DetalleCompra(id_compra=compra.id_compra, id_producto=productos[0].id_producto, cantidad=Decimal("10"), costo_unitario=Decimal("70"), subtotal=Decimal("700")))

    turno = Turno(id_usuario=cajero_user.id_usuario, id_terminal=terminal.id_terminal, fondo_inicial=Decimal("500.00"), estado="Abierto")
    db.session.add(turno)
    db.session.flush()
    db.session.add(MovimientoCaja(id_turno=turno.id_turno, id_usuario=cajero_user.id_usuario, tipo="Ingreso", concepto="Cambio adicional", monto=Decimal("200.00"), observacion="Demo"))

    canal_mesa = next(c for c in canales if c.nombre == "Mesa")
    canal_mostrador = next(c for c in canales if c.nombre == "Mostrador")
    efectivo = next(m for m in metodos if m.nombre == "Efectivo")
    tarjeta = next(m for m in metodos if m.nombre == "Tarjeta")

    pedido_pagado = Pedido(id_cliente=clientes[1].id_cliente, id_mesa=mesas[0].id_mesa, id_usuario=mesero_user.id_usuario, id_sucursal=sucursal.id_sucursal, id_canal=canal_mesa.id_canal, id_turno=turno.id_turno, estado="pagado", fecha=datetime.utcnow() - timedelta(hours=2), fecha_cierre=datetime.utcnow() - timedelta(hours=1, minutes=40))
    pedido_pagado.detalles.append(DetallePedido(id_producto=productos[0].id_producto, cantidad=Decimal("2"), precio_unitario=productos[0].precio, subtotal=Decimal("290.00")))
    pedido_pagado.detalles.append(DetallePedido(id_producto=productos[3].id_producto, cantidad=Decimal("2"), precio_unitario=productos[3].precio, subtotal=Decimal("70.00")))
    db.session.add(pedido_pagado)
    db.session.flush()
    recalcular_totales(pedido_pagado)
    db.session.add(Pago(id_pedido=pedido_pagado.id_pedido, id_metodo_pago=tarjeta.id_metodo_pago, id_turno=turno.id_turno, monto=pedido_pagado.total, referencia="DEMO-TARJETA"))

    pedido_cocina = Pedido(id_cliente=clientes[2].id_cliente, id_mesa=mesas[1].id_mesa, id_usuario=mesero_user.id_usuario, id_sucursal=sucursal.id_sucursal, id_canal=canal_mesa.id_canal, estado="en cocina", fecha=datetime.utcnow() - timedelta(minutes=25))
    pedido_cocina.detalles.append(DetallePedido(id_producto=productos[1].id_producto, cantidad=Decimal("1"), precio_unitario=productos[1].precio, subtotal=Decimal("180.00")))
    pedido_cocina.detalles.append(DetallePedido(id_producto=productos[4].id_producto, cantidad=Decimal("1"), precio_unitario=productos[4].precio, subtotal=Decimal("45.00")))
    db.session.add(pedido_cocina)
    mesas[1].estado = "ocupada"
    db.session.flush()
    recalcular_totales(pedido_cocina)

    pedido_pendiente = Pedido(id_cliente=clientes[0].id_cliente, id_usuario=cajero_user.id_usuario, id_sucursal=sucursal.id_sucursal, id_canal=canal_mostrador.id_canal, estado="pendiente", fecha=datetime.utcnow() - timedelta(minutes=10))
    pedido_pendiente.detalles.append(DetallePedido(id_producto=productos[5].id_producto, cantidad=Decimal("1"), precio_unitario=productos[5].precio, subtotal=Decimal("60.00")))
    db.session.add(pedido_pendiente)
    db.session.flush()
    recalcular_totales(pedido_pendiente)

    db.session.commit()


def generar_schema_sql():
    from sqlalchemy.schema import CreateTable
    import app.models  # noqa
    target = "schema.sql"
    statements = []
    for table in db.metadata.sorted_tables:
        statements.append(str(CreateTable(table).compile(db.engine)).strip() + ";")
    with open(target, "w", encoding="utf-8") as f:
        f.write("-- Schema DoomerPOS v4.0\n")
        f.write("-- Generado desde modelos SQLAlchemy\n\n")
        f.write("\n\n".join(statements))
