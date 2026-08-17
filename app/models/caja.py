from datetime import datetime
from app.extensions import db

class Turno(db.Model):
    __tablename__ = "turno"
    id_turno = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_terminal = db.Column(db.Integer, db.ForeignKey("terminal.id_terminal"), nullable=True)
    fecha_apertura = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    fondo_inicial = db.Column(db.Numeric(10, 2), default=0)
    estado = db.Column(db.String(20), default="Abierto")
    observacion_apertura = db.Column(db.String(255))

    usuario = db.relationship("Usuario", back_populates="turnos")
    terminal = db.relationship("Terminal", back_populates="turnos")
    pedidos = db.relationship("Pedido", back_populates="turno")
    pagos = db.relationship("Pago", back_populates="turno")
    movimientos = db.relationship("MovimientoCaja", back_populates="turno", cascade="all, delete-orphan")
    cierres = db.relationship("CierreCaja", back_populates="turno")

class MovimientoCaja(db.Model):
    __tablename__ = "movimiento_caja"
    id_movimiento_caja = db.Column(db.Integer, primary_key=True)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id_turno"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Ingreso, Egreso
    concepto = db.Column(db.String(120), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observacion = db.Column(db.String(255))

    turno = db.relationship("Turno", back_populates="movimientos")
    usuario = db.relationship("Usuario")

class CierreCaja(db.Model):
    __tablename__ = "cierre_caja"
    id_cierre = db.Column(db.Integer, primary_key=True)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id_turno"), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    total_efectivo = db.Column(db.Numeric(10, 2), default=0)
    total_tarjeta = db.Column(db.Numeric(10, 2), default=0)
    total_transferencia = db.Column(db.Numeric(10, 2), default=0)
    total_ingresos = db.Column(db.Numeric(10, 2), default=0)
    total_egresos = db.Column(db.Numeric(10, 2), default=0)
    total_sistema = db.Column(db.Numeric(10, 2), default=0)
    total_contado = db.Column(db.Numeric(10, 2), default=0)
    diferencia = db.Column(db.Numeric(10, 2), default=0)
    observacion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    turno = db.relationship("Turno", back_populates="cierres")
    usuario = db.relationship("Usuario")

class Autorizacion(db.Model):
    __tablename__ = "autorizacion"
    id_autorizacion = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), nullable=False)
    id_usuario_solicita = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_usuario_autoriza = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)
    motivo = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="Pendiente")

    solicitante = db.relationship("Usuario", foreign_keys=[id_usuario_solicita])
    autorizador = db.relationship("Usuario", foreign_keys=[id_usuario_autoriza])
