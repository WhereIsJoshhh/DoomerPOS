from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import (
    db, Rol, Sucursal, Usuario, Mesa, Cliente, CategoriaProducto,
    Producto, Pedido, DetallePedido, MetodoPago, Pago, Impuesto, Factura,
    Turno, CierreCaja, Almacen, Inventario, AuditoriaLog
)

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.cli.command("init-db")
def init_db():
    """Crea las tablas y carga datos base de prueba."""
    db.drop_all()
    db.create_all()
    admin = Rol(nombre="Administrador", descripcion="Permisos completos")
    gerente = Rol(nombre="Gerente/Supervisor", descripcion="Permisos de alto nivel")
    cajero = Rol(nombre="Cajero", descripcion="Caja y cobros")
    db.session.add_all([admin, gerente, cajero])
    sucursal = Sucursal(nombre="Sucursal Principal", direccion="Comayagua", telefono="0000-0000")
    db.session.add(sucursal)
    db.session.flush()
    user = Usuario(id_rol=admin.id_rol, id_sucursal=sucursal.id_sucursal, nombre="Administrador Demo", usuario_login="admin")
    mesa1 = Mesa(id_sucursal=sucursal.id_sucursal, numero_mesa="1", zona="Salón", estado="libre")
    cat = CategoriaProducto(nombre="Comidas", descripcion="Platos principales")
    mp = MetodoPago(nombre="Efectivo", descripcion="Pago en caja")
    imp = Impuesto(nombre="ISV", porcentaje=15)
    almacen = Almacen(id_sucursal=sucursal.id_sucursal, nombre="Almacén Principal", ubicacion="Cocina")
    db.session.add_all([user, mesa1, cat, mp, imp, almacen])
    db.session.flush()
    prod = Producto(id_categoria=cat.id_categoria, nombre="Hamburguesa clásica", precio=120, estado="activo")
    db.session.add(prod)
    db.session.flush()
    inv = Inventario(id_almacen=almacen.id_almacen, id_producto=prod.id_producto, existencia_actual=25, costo_promedio=55)
    db.session.add(inv)
    db.session.commit()
    print("Base de datos GastroPOS 360 creada con datos demo.")

@app.route("/")
def dashboard():
    total_pedidos = Pedido.query.count()
    total_productos = Producto.query.count()
    mesas_ocupadas = Mesa.query.filter_by(estado="ocupada").count()
    ventas_total = sum([float(p.total or 0) for p in Pedido.query.all()])
    return render_template("dashboard.html", total_pedidos=total_pedidos, total_productos=total_productos, mesas_ocupadas=mesas_ocupadas, ventas_total=ventas_total)

@app.route("/productos")
def productos():
    return render_template("productos.html", productos=Producto.query.all())

@app.route("/pedidos", methods=["GET", "POST"])
def pedidos():
    if request.method == "POST":
        producto = Producto.query.get_or_404(int(request.form["id_producto"]))
        mesa = Mesa.query.get(int(request.form.get("id_mesa") or 0))
        usuario = Usuario.query.first()
        sucursal = Sucursal.query.first()
        cliente = Cliente.query.filter_by(nombre="Cliente general").first()
        if not cliente:
            cliente = Cliente(nombre="Cliente general")
            db.session.add(cliente)
            db.session.flush()
        pedido = Pedido(id_cliente=cliente.id_cliente, id_mesa=mesa.id_mesa if mesa else None, id_usuario=usuario.id_usuario, id_sucursal=sucursal.id_sucursal, estado="abierto", total=producto.precio)
        db.session.add(pedido)
        db.session.flush()
        detalle = DetallePedido(id_pedido=pedido.id_pedido, id_producto=producto.id_producto, cantidad=1, precio_unitario=producto.precio, subtotal=producto.precio)
        db.session.add(detalle)
        if mesa:
            mesa.estado = "ocupada"
        db.session.add(AuditoriaLog(id_usuario=usuario.id_usuario, accion="Crear pedido", modulo="Pedidos", detalle=f"Pedido {pedido.id_pedido} creado"))
        db.session.commit()
        flash("Pedido creado y enviado a cocina/KDS.", "success")
        return redirect(url_for("pedidos"))
    return render_template("pedidos.html", pedidos=Pedido.query.order_by(Pedido.fecha.desc()).all(), productos=Producto.query.all(), mesas=Mesa.query.all())

@app.route("/mesas")
def mesas():
    return render_template("mesas.html", mesas=Mesa.query.all())

@app.route("/inventario")
def inventario():
    return render_template("inventario.html", inventarios=Inventario.query.all())

@app.route("/caja")
def caja():
    pedidos = Pedido.query.all()
    total = sum([float(p.total or 0) for p in pedidos])
    return render_template("caja.html", pedidos=pedidos, total=total)

@app.route("/reportes")
def reportes():
    pedidos = Pedido.query.all()
    ventas = sum([float(p.total or 0) for p in pedidos])
    return render_template("reportes.html", pedidos=pedidos, ventas=ventas)

if __name__ == "__main__":
    app.run(debug=True)
