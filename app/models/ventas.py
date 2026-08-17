from datetime import datetime
from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "cliente"
    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(120))
    estado = db.Column(db.String(20), default="Activo")

    pedidos = db.relationship("Pedido", back_populates="cliente")
    reservas = db.relationship("Reserva", back_populates="cliente")


class Reserva(db.Model):
    __tablename__ = "reserva"
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=False)
    id_mesa = db.Column(db.Integer, db.ForeignKey("mesa.id_mesa"), nullable=True)
    fecha_reserva = db.Column(db.DateTime, nullable=False)
    personas = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(20), default="Pendiente")  # Pendiente, Confirmada, Cancelada, Atendida
    notas = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("Cliente", back_populates="reservas")
    mesa = db.relationship("Mesa")


class Pedido(db.Model):
    __tablename__ = "pedido"
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"), nullable=True)
    id_mesa = db.Column(db.Integer, db.ForeignKey("mesa.id_mesa"), nullable=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    id_canal = db.Column(db.Integer, db.ForeignKey("canal_venta.id_canal"), nullable=False)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id_turno"), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(30), default="pendiente")  # pendiente, en cocina, listo, servido, pagado, cancelado
    prioridad = db.Column(db.String(20), default="normal")  # normal, alta
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    cargo_adicional = db.Column(db.Numeric(10, 2), default=0)
    impuesto = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    tipo_pago = db.Column(db.String(30), default="Sin pago")
    descuento_motivo = db.Column(db.String(255))
    notas = db.Column(db.String(255))

    cliente = db.relationship("Cliente", back_populates="pedidos")
    mesa = db.relationship("Mesa", back_populates="pedidos")
    usuario = db.relationship("Usuario", back_populates="pedidos")
    sucursal = db.relationship("Sucursal", back_populates="pedidos")
    canal = db.relationship("CanalVenta", back_populates="pedidos")
    turno = db.relationship("Turno", back_populates="pedidos")
    detalles = db.relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    pagos = db.relationship("Pago", back_populates="pedido", cascade="all, delete-orphan")
    facturas = db.relationship("Factura", back_populates="pedido", cascade="all, delete-orphan")

    @property
    def minutos_abierto(self):
        delta = (self.fecha_cierre or datetime.utcnow()) - self.fecha
        return max(0, int(delta.total_seconds() // 60))


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.String(255))

    pedido = db.relationship("Pedido", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles_pedido")


class MetodoPago(db.Model):
    __tablename__ = "metodo_pago"
    id_metodo_pago = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))

    pagos = db.relationship("Pago", back_populates="metodo_pago")


class Pago(db.Model):
    __tablename__ = "pago"
    id_pago = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey("metodo_pago.id_metodo_pago"), nullable=False)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id_turno"), nullable=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    referencia = db.Column(db.String(120))

    pedido = db.relationship("Pedido", back_populates="pagos")
    metodo_pago = db.relationship("MetodoPago", back_populates="pagos")
    turno = db.relationship("Turno", back_populates="pagos")


class Impuesto(db.Model):
    __tablename__ = "impuesto"
    id_impuesto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)

    facturas = db.relationship("Factura", back_populates="impuesto_rel")


class Factura(db.Model):
    __tablename__ = "factura"
    id_factura = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), nullable=False)
    id_impuesto = db.Column(db.Integer, db.ForeignKey("impuesto.id_impuesto"), nullable=False)
    numero_factura = db.Column(db.String(80), nullable=False, unique=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    cargo_adicional = db.Column(db.Numeric(10, 2), default=0)
    impuesto_total = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), default="Emitida")
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    pedido = db.relationship("Pedido", back_populates="facturas")
    impuesto_rel = db.relationship("Impuesto", back_populates="facturas")
