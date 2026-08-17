from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import Mesa, Pedido
from app.utils.security import login_required, require_permission
from app.services.auditoria_service import registrar_accion

bp = Blueprint("mesas", __name__, url_prefix="/mesas")


@bp.route("/")
@login_required
@require_permission("mesas.ver")
def index():
    zona = request.args.get("zona", "")
    query = Mesa.query
    if zona:
        query = query.filter(Mesa.zona == zona)
    mesas = query.order_by(Mesa.zona, Mesa.numero_mesa).all()
    zonas = [z[0] for z in db.session.query(Mesa.zona).distinct().order_by(Mesa.zona).all()]
    pedidos = Pedido.query.filter(Pedido.estado.in_(["pendiente", "en cocina", "listo", "servido"])).all()
    pedidos_por_mesa = {p.id_mesa: p for p in pedidos if p.id_mesa}
    resumen = {estado: Mesa.query.filter_by(estado=estado).count() for estado in ["libre", "ocupada", "reservada", "limpieza"]}
    return render_template("mesas/index.html", mesas=mesas, pedidos_por_mesa=pedidos_por_mesa, zonas=zonas, zona=zona, resumen=resumen)


@bp.post("/<int:id_mesa>/estado")
@login_required
@require_permission("mesas.gestionar")
def cambiar_estado(id_mesa):
    mesa = Mesa.query.get_or_404(id_mesa)
    estado = request.form.get("estado")
    notas = (request.form.get("notas") or "").strip()[:255]
    if estado not in {"libre", "ocupada", "reservada", "limpieza"}:
        flash("Estado de mesa no válido.", "danger")
        return redirect(url_for("mesas.index"))
    if estado == "libre" and Pedido.query.filter_by(id_mesa=id_mesa).filter(Pedido.estado.in_(["pendiente", "en cocina", "listo", "servido"])).first():
        flash("No se puede liberar una mesa con pedido abierto.", "warning")
        return redirect(url_for("mesas.index"))
    mesa.estado = estado
    mesa.notas = notas or mesa.notas
    mesa.actualizado_en = datetime.utcnow()
    registrar_accion("Cambiar estado de mesa", "Mesas", f"Mesa {mesa.numero_mesa}: {estado}")
    db.session.commit()
    flash("Estado de mesa actualizado.", "success")
    return redirect(url_for("mesas.index"))
