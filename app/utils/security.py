from functools import wraps
from flask import session, redirect, url_for, flash, g, request, abort
from app.models import Usuario
from app.utils.permissions import menu_para_usuario


def cargar_usuario_actual():
    g.usuario = None
    usuario_id = session.get("usuario_id")
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)
        if usuario and usuario.estado == "Activo":
            g.usuario = usuario
            g.menu_items = menu_para_usuario(usuario)
        else:
            session.clear()
    else:
        g.menu_items = []


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.get("usuario") is None:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)
    return wrapped_view


def require_permission(codigo_permiso):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            usuario = g.get("usuario")
            if usuario is None:
                flash("Debes iniciar sesión para continuar.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if not usuario.puede(codigo_permiso):
                flash("Acceso denegado. Tu rol no tiene permiso para esta sección.", "danger")
                abort(403)
            return view(**kwargs)
        return wrapped_view
    return decorator


def require_any_permission(*codigos_permiso):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            usuario = g.get("usuario")
            if usuario is None:
                flash("Debes iniciar sesión para continuar.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if not any(usuario.puede(codigo) for codigo in codigos_permiso):
                flash("Acceso denegado. Tu rol no tiene permiso para esta sección.", "danger")
                abort(403)
            return view(**kwargs)
        return wrapped_view
    return decorator


def usuario_puede(codigo_permiso: str) -> bool:
    usuario = g.get("usuario")
    return bool(usuario and usuario.puede(codigo_permiso))
