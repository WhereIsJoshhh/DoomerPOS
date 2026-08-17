from flask import request, g
from app.extensions import db
from app.models import AuditoriaLog


def registrar_accion(accion: str, modulo: str, detalle: str = "") -> None:
    usuario = g.get("usuario") if g else None
    log = AuditoriaLog(
        id_usuario=usuario.id_usuario if usuario else None,
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        ip=request.remote_addr if request else None,
        user_agent=(request.headers.get("User-Agent", "")[:255] if request else None),
    )
    db.session.add(log)
