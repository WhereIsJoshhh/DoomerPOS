from datetime import datetime
from app.extensions import db

class AuditoriaLog(db.Model):
    __tablename__ = "auditoria_log"
    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)
    accion = db.Column(db.String(120), nullable=False)
    modulo = db.Column(db.String(80), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    detalle = db.Column(db.Text)
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))

    usuario = db.relationship("Usuario", back_populates="auditorias")
