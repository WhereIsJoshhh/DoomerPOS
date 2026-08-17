from datetime import datetime, time, date, timedelta
from decimal import Decimal
from flask import Blueprint, render_template, request
from sqlalchemy import func
from app.extensions import db
from app.models import Pedido, DetallePedido, Producto, Inventario, CierreCaja, Pago, MetodoPago, Merma, Usuario, MovimientoCaja, Compra
from app.utils.security import login_required, require_any_permission

bp = Blueprint("reportes", __name__, url_prefix="/reportes")


def rango_fechas():
    desde_txt = request.args.get("desde")
    hasta_txt = request.args.get("hasta")
    try:
        desde = datetime.combine(datetime.strptime(desde_txt, "%Y-%m-%d").date(), time.min) if desde_txt else datetime.combine(date.today(), time.min)
        hasta = datetime.combine(datetime.strptime(hasta_txt, "%Y-%m-%d").date(), time.max) if hasta_txt else datetime.combine(date.today(), time.max)
    except ValueError:
        desde = datetime.combine(date.today(), time.min)
        hasta = datetime.combine(date.today(), time.max)
    return desde, hasta


@bp.route("/")
@login_required
@require_any_permission("reportes.ver", "reportes.caja")
def index():
    desde, hasta = rango_fechas()
    ventas = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta)).scalar() or Decimal("0")
    descuentos = db.session.query(func.coalesce(func.sum(Pedido.descuento), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta)).scalar() or Decimal("0")
    cargos = db.session.query(func.coalesce(func.sum(Pedido.cargo_adicional), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta)).scalar() or Decimal("0")
    pedidos_pagados = Pedido.query.filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta)).count()
    pedidos_cancelados = Pedido.query.filter(Pedido.estado == "cancelado", Pedido.fecha.between(desde, hasta)).count()
    ticket_promedio = (Decimal(ventas) / pedidos_pagados).quantize(Decimal("0.01")) if pedidos_pagados else Decimal("0")
    ventas_por_pago = (
        db.session.query(MetodoPago.nombre, func.coalesce(func.sum(Pago.monto), 0))
        .join(Pago, Pago.id_metodo_pago == MetodoPago.id_metodo_pago)
        .filter(Pago.fecha_pago.between(desde, hasta))
        .group_by(MetodoPago.nombre)
        .all()
    )
    ventas_por_usuario = (
        db.session.query(Usuario.nombre, func.coalesce(func.sum(Pedido.total), 0), func.count(Pedido.id_pedido))
        .join(Pedido, Pedido.id_usuario == Usuario.id_usuario)
        .filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta))
        .group_by(Usuario.nombre)
        .order_by(func.sum(Pedido.total).desc())
        .all()
    )
    top_productos = (
        db.session.query(Producto.nombre, func.sum(DetallePedido.cantidad).label("cantidad"), func.sum(DetallePedido.subtotal).label("total"))
        .join(DetallePedido, DetallePedido.id_producto == Producto.id_producto)
        .join(Pedido, Pedido.id_pedido == DetallePedido.id_pedido)
        .filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(desde, hasta))
        .group_by(Producto.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .limit(10)
        .all()
    )
    inventario = Inventario.query.order_by(Inventario.existencia_actual.asc()).all()
    cierres = CierreCaja.query.filter(CierreCaja.fecha.between(desde, hasta)).order_by(CierreCaja.fecha.desc()).all()
    movimientos_caja = MovimientoCaja.query.filter(MovimientoCaja.fecha.between(desde, hasta)).order_by(MovimientoCaja.fecha.desc()).limit(30).all()
    mermas = Merma.query.filter(Merma.fecha.between(desde, hasta)).order_by(Merma.fecha.desc()).all()
    compras = Compra.query.filter(Compra.fecha.between(desde, hasta)).order_by(Compra.fecha.desc()).all()
    ventas_semana = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        ini, end = datetime.combine(d, time.min), datetime.combine(d, time.max)
        total = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(ini, end)).scalar() or Decimal("0")
        ventas_semana.append((d.strftime("%d/%m"), total))
    return render_template("reportes/index.html", desde=desde.date(), hasta=hasta.date(), ventas=ventas, descuentos=descuentos, cargos=cargos, pedidos_pagados=pedidos_pagados, pedidos_cancelados=pedidos_cancelados, ticket_promedio=ticket_promedio, ventas_por_pago=ventas_por_pago, ventas_por_usuario=ventas_por_usuario, top_productos=top_productos, inventario=inventario, cierres=cierres, movimientos_caja=movimientos_caja, mermas=mermas, compras=compras, ventas_semana=ventas_semana)
