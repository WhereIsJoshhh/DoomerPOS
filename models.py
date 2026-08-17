from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = "rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    usuarios = db.relationship("Usuario", back_populates="rol")

class Sucursal(db.Model):
    __tablename__ = "sucursal"
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(30))
    usuarios = db.relationship("Usuario", back_populates="sucursal")
    terminales = db.relationship("Terminal", back_populates="sucursal")
    mesas = db.relationship("Mesa", back_populates="sucursal")
    almacenes = db.relationship("Almacen", back_populates="sucursal")
    pedidos = db.relationship("Pedido", back_populates="sucursal")

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    usuario_login = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False, default="demo")
    estado = db.Column(db.String(20), default="activo")
    rol = db.relationship("Rol", back_populates="usuarios")
    sucursal = db.relationship("Sucursal", back_populates="usuarios")
    pedidos = db.relationship("Pedido", back_populates="usuario")
    turnos = db.relationship("Turno", back_populates="usuario")
    cierres = db.relationship("CierreCaja", back_populates="usuario")
    logs = db.relationship("AuditoriaLog", back_populates="usuario")

class Terminal(db.Model):
    __tablename__ = "terminal"
    id_terminal = db.Column(db.Integer, primary_key=True)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    codigo_terminal = db.Column(db.String(80), nullable=False)
    estado = db.Column(db.String(20), default="activa")
    sucursal = db.relationship("Sucursal", back_populates="terminales")

class Mesa(db.Model):
    __tablename__ = "mesa"
    id_mesa = db.Column(db.Integer, primary_key=True)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    numero_mesa = db.Column(db.String(20), nullable=False)
    zona = db.Column(db.String(80))
    estado = db.Column(db.String(20), default="libre")
    sucursal = db.relationship("Sucursal", back_populates="mesas")
    pedidos = db.relationship("Pedido", back_populates="mesa")

class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(120))
    pedidos = db.relationship("Pedido", back_populates="cliente")

class CategoriaProducto(db.Model):
    __tablename__ = "categoria_producto"
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(255))
    productos = db.relationship("Producto", back_populates="categoria")

class Producto(db.Model):
    __tablename__ = "producto"
    id_producto = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria_producto.id_categoria"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default="activo")
    categoria = db.relationship("CategoriaProducto", back_populates="productos")
    detalles = db.relationship("DetallePedido", back_populates="producto")
    modificadores = db.relationship("Modificador", back_populates="producto")
    recetas = db.relationship("Receta", back_populates="producto")
    inventarios = db.relationship("Inventario", back_populates="producto")
    mermas = db.relationship("Merma", back_populates="producto")

class Modificador(db.Model):
    __tablename__ = "modificador"
    id_modificador = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    precio_extra = db.Column(db.Numeric(10, 2), default=0)
    producto = db.relationship("Producto", back_populates="modificadores")

class Ingrediente(db.Model):
    __tablename__ = "ingrediente"
    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    unidad_medida = db.Column(db.String(30), nullable=False)
    stock_minimo = db.Column(db.Numeric(10, 2), default=0)
    recetas = db.relationship("Receta", back_populates="ingrediente")

class Receta(db.Model):
    __tablename__ = "receta"
    id_receta = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=False)
    cantidad_requerida = db.Column(db.Numeric(10, 3), nullable=False)
    producto = db.relationship("Producto", back_populates="recetas")
    ingrediente = db.relationship("Ingrediente", back_populates="recetas")

class Almacen(db.Model):
    __tablename__ = "almacen"
    id_almacen = db.Column(db.Integer, primary_key=True)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    ubicacion = db.Column(db.String(255))
    sucursal = db.relationship("Sucursal", back_populates="almacenes")
    inventarios = db.relationship("Inventario", back_populates="almacen")
    compras = db.relationship("Compra", back_populates="almacen")
    mermas = db.relationship("Merma", back_populates="almacen")

class Inventario(db.Model):
    __tablename__ = "inventario"
    id_inventario = db.Column(db.Integer, primary_key=True)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    existencia_actual = db.Column(db.Numeric(10, 3), default=0)
    costo_promedio = db.Column(db.Numeric(10, 2), default=0)
    almacen = db.relationship("Almacen", back_populates="inventarios")
    producto = db.relationship("Producto", back_populates="inventarios")

class Proveedor(db.Model):
    __tablename__ = "proveedor"
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(120))
    compras = db.relationship("Compra", back_populates="proveedor")

class Compra(db.Model):
    __tablename__ = "compra"
    id_compra = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"), nullable=False)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total_compra = db.Column(db.Numeric(10, 2), default=0)
    proveedor = db.relationship("Proveedor", back_populates="compras")
    almacen = db.relationship("Almacen", back_populates="compras")

class Pedido(db.Model):
    __tablename__ = "pedido"
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=True)
    id_mesa = db.Column(db.Integer, db.ForeignKey("mesa.id_mesa"), nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="abierto")
    total = db.Column(db.Numeric(10, 2), default=0)
    cliente = db.relationship("Cliente", back_populates="pedidos")
    mesa = db.relationship("Mesa", back_populates="pedidos")
    usuario = db.relationship("Usuario", back_populates="pedidos")
    sucursal = db.relationship("Sucursal", back_populates="pedidos")
    detalles = db.relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    pagos = db.relationship("Pago", back_populates="pedido")
    facturas = db.relationship("Factura", back_populates="pedido")

class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    pedido = db.relationship("Pedido", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles")

class MetodoPago(db.Model):
    __tablename__ = "metodo_pago"
    id_metodo_pago = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(255))
    pagos = db.relationship("Pago", back_populates="metodo_pago")

class Pago(db.Model):
    __tablename__ = "pago"
    id_pago = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey("metodo_pago.id_metodo_pago"), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    pedido = db.relationship("Pedido", back_populates="pagos")
    metodo_pago = db.relationship("MetodoPago", back_populates="pagos")

class Impuesto(db.Model):
    __tablename__ = "impuesto"
    id_impuesto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)
    facturas = db.relationship("Factura", back_populates="impuesto")

class Factura(db.Model):
    __tablename__ = "factura"
    id_factura = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_impuesto = db.Column(db.Integer, db.ForeignKey("impuesto.id_impuesto"), nullable=False)
    numero_factura = db.Column(db.String(50), nullable=False, unique=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    impuesto_total = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    pedido = db.relationship("Pedido", back_populates="facturas")
    impuesto = db.relationship("Impuesto", back_populates="facturas")

class Turno(db.Model):
    __tablename__ = "turno"
    id_turno = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_apertura = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime)
    fondo_inicial = db.Column(db.Numeric(10, 2), default=0)
    usuario = db.relationship("Usuario", back_populates="turnos")
    cierres = db.relationship("CierreCaja", back_populates="turno")

class CierreCaja(db.Model):
    __tablename__ = "cierre_caja"
    id_cierre = db.Column(db.Integer, primary_key=True)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id_turno"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    total_efectivo = db.Column(db.Numeric(10, 2), default=0)
    total_tarjeta = db.Column(db.Numeric(10, 2), default=0)
    diferencia = db.Column(db.Numeric(10, 2), default=0)
    turno = db.relationship("Turno", back_populates="cierres")
    usuario = db.relationship("Usuario", back_populates="cierres")

class Merma(db.Model):
    __tablename__ = "merma"
    id_merma = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 3), nullable=False)
    motivo = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    producto = db.relationship("Producto", back_populates="mermas")
    almacen = db.relationship("Almacen", back_populates="mermas")

class AuditoriaLog(db.Model):
    __tablename__ = "auditoria_log"
    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    accion = db.Column(db.String(120), nullable=False)
    modulo = db.Column(db.String(80), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    detalle = db.Column(db.Text)
    usuario = db.relationship("Usuario", back_populates="logs")
