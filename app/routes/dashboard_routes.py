from datetime import date, datetime, time, timedelta
from decimal import Decimal
from flask import Blueprint, render_template, g
from sqlalchemy import func
from app.extensions import db
from app.models import Pedido, Mesa, Producto, Inventario, CierreCaja, AuditoriaLog, Pago, DetallePedido, Usuario
from app.services.caja_service import obtener_turno_activo, resumen_turno
from app.services.inventario_service import productos_bajo_stock
from app.utils.security import login_required, require_permission

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
@require_permission("dashboard.ver")
def index():
    inicio = datetime.combine(date.today(), time.min)
    fin = datetime.combine(date.today(), time.max)
    hace_30 = datetime.utcnow() - timedelta(days=30)
    ventas_dia = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(inicio, fin)).scalar() or Decimal("0")
    pedidos_hoy = Pedido.query.filter(Pedido.fecha.between(inicio, fin)).count()
    pedidos_abiertos = Pedido.query.filter(Pedido.estado.in_(["pendiente", "en cocina", "listo", "servido"])).count()
    mesas_ocupadas = Mesa.query.filter(Mesa.estado == "ocupada").count()
    mesas_limpieza = Mesa.query.filter(Mesa.estado == "limpieza").count()
    alertas = productos_bajo_stock()
    alertas_stock = len(alertas)
    top_productos = (
        db.session.query(Producto.nombre, func.coalesce(func.sum(DetallePedido.cantidad), 0).label("cantidad"), func.coalesce(func.sum(DetallePedido.subtotal), 0).label("total"))
        .join(DetallePedido, DetallePedido.id_producto == Producto.id_producto)
        .join(Pedido, Pedido.id_pedido == DetallePedido.id_pedido)
        .filter(Pedido.estado == "pagado", Pedido.fecha_cierre >= hace_30)
        .group_by(Producto.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .limit(5)
        .all()
    )
    ventas_por_usuario = (
        db.session.query(Usuario.nombre, func.coalesce(func.sum(Pedido.total), 0).label("total"), func.count(Pedido.id_pedido).label("pedidos"))
        .join(Pedido, Pedido.id_usuario == Usuario.id_usuario)
        .filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(inicio, fin))
        .group_by(Usuario.nombre)
        .order_by(func.sum(Pedido.total).desc())
        .limit(5)
        .all()
    )
    ventas_semana = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        ini = datetime.combine(d, time.min)
        end = datetime.combine(d, time.max)
        total = db.session.query(func.coalesce(func.sum(Pedido.total), 0)).filter(Pedido.estado == "pagado", Pedido.fecha_cierre.between(ini, end)).scalar() or Decimal("0")
        ventas_semana.append((d.strftime("%d/%m"), total))
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).limit(5).all()
    auditoria = AuditoriaLog.query.order_by(AuditoriaLog.fecha_hora.desc()).limit(6).all()
    turno = obtener_turno_activo(g.usuario.id_usuario)
    resumen = resumen_turno(turno)
    return render_template("dashboard/index.html", ventas_dia=ventas_dia, pedidos_hoy=pedidos_hoy, pedidos_abiertos=pedidos_abiertos, mesas_ocupadas=mesas_ocupadas, mesas_limpieza=mesas_limpieza, alertas_stock=alertas_stock, alertas=alertas[:5], top_productos=top_productos, ventas_por_usuario=ventas_por_usuario, ventas_semana=ventas_semana, cierres=cierres, auditoria=auditoria, turno=turno, resumen=resumen)
