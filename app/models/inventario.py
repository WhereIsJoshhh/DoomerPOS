from datetime import datetime
from app.extensions import db

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
    existencia_actual = db.Column(db.Numeric(10, 2), default=0)
    costo_promedio = db.Column(db.Numeric(10, 2), default=0)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("id_almacen", "id_producto", name="uq_inventario_almacen_producto"),)

    almacen = db.relationship("Almacen", back_populates="inventarios")
    producto = db.relationship("Producto", back_populates="inventarios")

class MovimientoInventario(db.Model):
    __tablename__ = "movimiento_inventario"
    id_movimiento = db.Column(db.Integer, primary_key=True)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # Entrada, Salida, Ajuste, Venta, Merma
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    motivo = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    almacen = db.relationship("Almacen")
    producto = db.relationship("Producto")
    usuario = db.relationship("Usuario")

class Proveedor(db.Model):
    __tablename__ = "proveedor"
    id_proveedor = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(30))
    correo = db.Column(db.String(120))
    contacto = db.Column(db.String(120))
    estado = db.Column(db.String(20), default="Activo")

    compras = db.relationship("Compra", back_populates="proveedor")

class Compra(db.Model):
    __tablename__ = "compra"
    id_compra = db.Column(db.Integer, primary_key=True)
    id_proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.id_proveedor"), nullable=False)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total_compra = db.Column(db.Numeric(10, 2), default=0)
    estado = db.Column(db.String(20), default="Registrada")
    observacion = db.Column(db.String(255))

    proveedor = db.relationship("Proveedor", back_populates="compras")
    almacen = db.relationship("Almacen", back_populates="compras")
    detalles = db.relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")

class DetalleCompra(db.Model):
    __tablename__ = "detalle_compra"
    id_detalle_compra = db.Column(db.Integer, primary_key=True)
    id_compra = db.Column(db.Integer, db.ForeignKey("compra.id_compra"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    compra = db.relationship("Compra", back_populates="detalles")
    producto = db.relationship("Producto")

class Merma(db.Model):
    __tablename__ = "merma"
    id_merma = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    id_almacen = db.Column(db.Integer, db.ForeignKey("almacen.id_almacen"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship("Producto", back_populates="mermas")
    almacen = db.relationship("Almacen", back_populates="mermas")
    usuario = db.relationship("Usuario")
