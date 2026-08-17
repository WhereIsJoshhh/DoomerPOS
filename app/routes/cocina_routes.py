from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Pedido
from app.utils.security import login_required, require_permission
from app.services.pedidos_service import cambiar_estado_pedido
from app.services.auditoria_service import registrar_accion

bp = Blueprint("cocina", __name__, url_prefix="/cocina")


@bp.route("/")
@login_required
@require_permission("cocina.operar")
def index():
    estado = request.args.get("estado", "todos")
    estados = ["en cocina", "listo", "servido"]
    query = Pedido.query.filter(Pedido.estado.in_(estados))
    if estado in estados:
        query = query.filter(Pedido.estado == estado)
    pedidos = query.order_by(Pedido.prioridad.desc(), Pedido.fecha.asc()).all()
    columnas = {e: [p for p in pedidos if p.estado == e] for e in estados}
    return render_template("cocina/index.html", pedidos=pedidos, columnas=columnas, estado=estado, estados=estados)


@bp.post("/<int:id_pedido>/<accion>")
@login_required
@require_permission("cocina.operar")
def cambiar_estado(id_pedido, accion):
    mapa = {"listo": "listo", "servido": "servido", "en-cocina": "en cocina"}
    pedido = Pedido.query.get_or_404(id_pedido)
    if accion not in mapa:
        flash("Acción no válida.", "danger")
        return redirect(url_for("cocina.index"))
    try:
        cambiar_estado_pedido(pedido, mapa[accion])
        registrar_accion("Actualizar KDS", "Cocina/KDS", f"Pedido #{pedido.id_pedido}: {pedido.estado}")
        db.session.commit()
        flash("Estado actualizado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("cocina.index", estado=pedido.estado))
