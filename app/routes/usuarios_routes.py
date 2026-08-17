from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Usuario, Rol, Sucursal
from app.utils.security import login_required, require_permission
from app.utils.validators import requerido, limpiar_texto, validar_password_seguro
from app.services.auditoria_service import registrar_accion

bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@bp.route("/")
@login_required
@require_permission("usuarios.gestionar")
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    roles = Rol.query.order_by(Rol.nombre).all()
    sucursales = Sucursal.query.order_by(Sucursal.nombre).all()
    return render_template("usuarios/index.html", usuarios=usuarios, roles=roles, sucursales=sucursales)

@bp.post("/")
@login_required
@require_permission("usuarios.gestionar")
def crear():
    try:
        password = validar_password_seguro(request.form.get("password", ""))
        usuario = Usuario(
            nombre=requerido(request.form.get("nombre"), "nombre"),
            usuario_login=requerido(request.form.get("usuario_login"), "usuario").lower(),
            id_rol=int(request.form.get("id_rol")),
            id_sucursal=int(request.form.get("id_sucursal")),
            estado=request.form.get("estado", "Activo"),
        )
        usuario.set_password(password)
        db.session.add(usuario)
        registrar_accion("Crear usuario", "Usuarios", usuario.usuario_login)
        db.session.commit()
        flash("Usuario creado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("usuarios.index"))

@bp.post("/<int:id_usuario>/estado")
@login_required
@require_permission("usuarios.gestionar")
def estado(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    nuevo = request.form.get("estado")
    if nuevo not in {"Activo", "Inactivo"}:
        flash("Estado inválido.", "danger")
        return redirect(url_for("usuarios.index"))
    usuario.estado = nuevo
    registrar_accion("Cambiar estado usuario", "Usuarios", f"{usuario.usuario_login}: {nuevo}")
    db.session.commit()
    flash("Estado actualizado.", "success")
    return redirect(url_for("usuarios.index"))
