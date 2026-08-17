from datetime import datetime
from app.extensions import db

class Sucursal(db.Model):
    __tablename__ = "sucursal"
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(30))
    estado = db.Column(db.String(20), default="Activa")

    usuarios = db.relationship("Usuario", back_populates="sucursal")
    terminales = db.relationship("Terminal", back_populates="sucursal")
    mesas = db.relationship("Mesa", back_populates="sucursal")
    almacenes = db.relationship("Almacen", back_populates="sucursal")
    pedidos = db.relationship("Pedido", back_populates="sucursal")

class Terminal(db.Model):
    __tablename__ = "terminal"
    id_terminal = db.Column(db.Integer, primary_key=True)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    codigo_terminal = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), default="POS")
    estado = db.Column(db.String(20), default="Activa")

    sucursal = db.relationship("Sucursal", back_populates="terminales")
    turnos = db.relationship("Turno", back_populates="terminal")

class Mesa(db.Model):
    __tablename__ = "mesa"
    id_mesa = db.Column(db.Integer, primary_key=True)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    numero_mesa = db.Column(db.String(20), nullable=False)
    zona = db.Column(db.String(80), default="Salón")
    capacidad = db.Column(db.Integer, default=4)
    estado = db.Column(db.String(20), default="libre")  # libre, ocupada, reservada, limpieza
    notas = db.Column(db.String(255))
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow)

    sucursal = db.relationship("Sucursal", back_populates="mesas")
    pedidos = db.relationship("Pedido", back_populates="mesa")

class CanalVenta(db.Model):
    __tablename__ = "canal_venta"
    id_canal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))

    pedidos = db.relationship("Pedido", back_populates="canal")
