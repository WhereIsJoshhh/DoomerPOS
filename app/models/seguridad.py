from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.utils.permissions import permisos_para_rol

class RolPermiso(db.Model):
    __tablename__ = "rol_permiso"
    id_rol_permiso = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    id_permiso = db.Column(db.Integer, db.ForeignKey("permiso.id_permiso"), nullable=False)
    __table_args__ = (db.UniqueConstraint("id_rol", "id_permiso", name="uq_rol_permiso"),)

class Rol(db.Model):
    __tablename__ = "rol"
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    estado = db.Column(db.String(20), default="Activo")
    usuarios = db.relationship("Usuario", back_populates="rol")
    permisos = db.relationship("Permiso", secondary="rol_permiso", back_populates="roles")

    def tiene_permiso(self, codigo: str) -> bool:
        return any(p.codigo == codigo for p in self.permisos)

class Permiso(db.Model):
    __tablename__ = "permiso"
    id_permiso = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(120), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))
    roles = db.relationship("Rol", secondary="rol_permiso", back_populates="permisos")

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey("rol.id_rol"), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey("sucursal.id_sucursal"), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    usuario_login = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(20), default="Activo")
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    rol = db.relationship("Rol", back_populates="usuarios")
    sucursal = db.relationship("Sucursal", back_populates="usuarios")
    pedidos = db.relationship("Pedido", back_populates="usuario")
    turnos = db.relationship("Turno", back_populates="usuario")
    auditorias = db.relationship("AuditoriaLog", back_populates="usuario")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def puede(self, codigo_permiso: str) -> bool:
        if self.estado != "Activo" or not self.rol:
            return False
        return self.rol.tiene_permiso(codigo_permiso) or codigo_permiso in permisos_para_rol(self.rol.nombre)

    def esta_bloqueado(self) -> bool:
        return self.bloqueado_hasta is not None and self.bloqueado_hasta > datetime.utcnow()
