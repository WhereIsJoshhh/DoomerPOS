from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db
from app.models import Usuario
from app.services.auditoria_service import registrar_accion
from app.utils.permissions import primer_endpoint_permitido

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_id"):
        usuario = Usuario.query.get(session["usuario_id"])
        return redirect(url_for(primer_endpoint_permitido(usuario)))
    if request.method == "POST":
        usuario_login = request.form.get("usuario_login", "").strip().lower()
        password = request.form.get("password", "")
        usuario = Usuario.query.filter_by(usuario_login=usuario_login).first()
        if usuario and usuario.esta_bloqueado():
            flash("Usuario bloqueado temporalmente por intentos fallidos. Intenta más tarde.", "danger")
            return render_template("auth/login.html")
        if not usuario or usuario.estado != "Activo" or not usuario.check_password(password):
            if usuario:
                usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
                if usuario.intentos_fallidos >= current_app.config["MAX_LOGIN_ATTEMPTS"]:
                    usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=current_app.config["LOGIN_BLOCK_MINUTES"])
                db.session.commit()
            flash("Credenciales inválidas.", "danger")
            return render_template("auth/login.html")
        session.clear()
        session.permanent = True
        session["usuario_id"] = usuario.id_usuario
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.ultimo_acceso = datetime.utcnow()
        registrar_accion("Inicio de sesión", "Seguridad", f"Usuario {usuario.usuario_login}")
        db.session.commit()
        next_url = request.args.get("next")
        if next_url and (not next_url.startswith("/") or next_url.startswith("//")):
            next_url = None
        return redirect(next_url or url_for(primer_endpoint_permitido(usuario)))
    return render_template("auth/login.html")

@bp.post("/logout")
def logout():
    registrar_accion("Cierre de sesión", "Seguridad", "Salida del sistema")
    db.session.commit()
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
