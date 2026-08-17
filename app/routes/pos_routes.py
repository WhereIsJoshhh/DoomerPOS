from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import Pedido, Producto, Mesa, Cliente, CanalVenta, MetodoPago
from app.utils.security import login_required, require_permission, require_any_permission
from app.utils.validators import decimal_positivo, decimal_no_negativo, entero_opcional, limpiar_texto
from app.services.pedidos_service import (
    crear_pedido,
    agregar_producto_a_pedido,
    aplicar_ajustes_pedido,
    enviar_a_cocina,
    cobrar_pedido,
    cobrar_pedido_mixto,
    cancelar_pedido,
)
from app.services.caja_service import obtener_turno_activo
from app.services.auditoria_service import registrar_accion

bp = Blueprint("pos", __name__, url_prefix="/pos")


@bp.route("/")
@login_required
@require_any_permission("pos.operar", "pedidos.ver")
def index():
    estado = request.args.get("estado", "activos")
    q = request.args.get("q", "").strip()
    base = Pedido.query
    if estado == "activos":
        base = base.filter(Pedido.estado.in_(["pendiente", "en cocina", "listo", "servido"]))
    elif estado in ["pendiente", "en cocina", "listo", "servido", "pagado", "cancelado"]:
        base = base.filter(Pedido.estado == estado)
    if q:
        if q.isdigit():
            base = base.filter(Pedido.id_pedido == int(q))
        else:
            base = base.join(Cliente, isouter=True).filter(Cliente.nombre.ilike(f"%{q}%"))
    pedidos = base.order_by(Pedido.fecha.desc()).limit(50).all()
    productos = Producto.query.filter_by(estado="Activo").order_by(Producto.nombre).all()
    mesas = Mesa.query.order_by(Mesa.zona, Mesa.numero_mesa).all()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    canales = CanalVenta.query.order_by(CanalVenta.nombre).all()
    metodos = MetodoPago.query.order_by(MetodoPago.nombre).all()
    turno = obtener_turno_activo(g.usuario.id_usuario)
    return render_template("pos/index.html", pedidos=pedidos, productos=productos, mesas=mesas, clientes=clientes, canales=canales, metodos=metodos, turno=turno, estado=estado, q=q)


@bp.post("/pedido")
@login_required
@require_permission("pos.operar")
def nuevo_pedido():
    try:
        id_mesa = entero_opcional(request.form.get("id_mesa"))
        id_cliente = entero_opcional(request.form.get("id_cliente"))
        id_canal = int(request.form.get("id_canal"))
        prioridad = request.form.get("prioridad", "normal")
        notas = limpiar_texto(request.form.get("notas"), 255)
        pedido = crear_pedido(g.usuario.id_usuario, g.usuario.id_sucursal, id_canal, id_cliente=id_cliente, id_mesa=id_mesa, notas=notas, prioridad=prioridad)
        registrar_accion("Crear pedido", "POS", f"Pedido #{pedido.id_pedido}")
        db.session.commit()
        flash("Pedido creado correctamente.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))


@bp.post("/pedido/<int:id_pedido>/agregar")
@login_required
@require_permission("pos.operar")
def agregar_producto(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        id_producto = int(request.form.get("id_producto"))
        cantidad = decimal_positivo(request.form.get("cantidad", "1"), "cantidad")
        notas = limpiar_texto(request.form.get("notas"), 255)
        agregar_producto_a_pedido(pedido, id_producto, cantidad, notas)
        registrar_accion("Agregar producto", "POS", f"Pedido #{pedido.id_pedido}, producto {id_producto}, cantidad {cantidad}")
        db.session.commit()
        flash("Producto agregado al pedido.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))


@bp.post("/pedido/<int:id_pedido>/ajustes")
@login_required
@require_permission("descuento.aprobar")
def ajustes(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        descuento = decimal_no_negativo(request.form.get("descuento", "0"), "descuento")
        cargo = decimal_no_negativo(request.form.get("cargo_adicional", "0"), "cargo adicional")
        motivo = limpiar_texto(request.form.get("motivo"), 255)
        if descuento and not motivo:
            raise ValueError("Para aplicar descuento debe indicar un motivo.")
        aplicar_ajustes_pedido(pedido, descuento, cargo, motivo)
        registrar_accion("Ajustar pedido", "POS", f"Pedido #{pedido.id_pedido}. Descuento L {descuento}, cargo L {cargo}")
        db.session.commit()
        flash("Descuento/cargo actualizado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))


@bp.post("/pedido/<int:id_pedido>/enviar-cocina")
@login_required
@require_permission("pos.operar")
def enviar_cocina(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        enviar_a_cocina(pedido)
        registrar_accion("Enviar a cocina", "POS", f"Pedido #{pedido.id_pedido}")
        db.session.commit()
        flash("Pedido enviado a cocina/KDS.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))


@bp.post("/pedido/<int:id_pedido>/pagar")
@login_required
@require_permission("pedidos.cobrar")
def pagar(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        turno = obtener_turno_activo(g.usuario.id_usuario)
        if not turno:
            raise ValueError("Debes abrir un turno de caja antes de cobrar.")
        metodo_nombre = request.form.get("metodo_nombre", "")
        referencia = limpiar_texto(request.form.get("referencia"), 120)
        if metodo_nombre == "Mixto":
            pagos = {
                "Efectivo": decimal_no_negativo(request.form.get("pago_efectivo", "0"), "pago efectivo"),
                "Tarjeta": decimal_no_negativo(request.form.get("pago_tarjeta", "0"), "pago tarjeta"),
                "Transferencia": decimal_no_negativo(request.form.get("pago_transferencia", "0"), "pago transferencia"),
            }
            cobrar_pedido_mixto(pedido, pagos, g.usuario.id_usuario, turno.id_turno, referencia)
        else:
            id_metodo_pago = int(request.form.get("id_metodo_pago"))
            monto = request.form.get("monto") or pedido.total
            cobrar_pedido(pedido, id_metodo_pago, Decimal(monto), g.usuario.id_usuario, turno.id_turno, referencia)
        registrar_accion("Cobrar pedido", "POS/Caja", f"Pedido #{pedido.id_pedido}, total L {pedido.total}, tipo {pedido.tipo_pago}")
        db.session.commit()
        flash("Pedido pagado. Inventario actualizado y factura emitida.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))


@bp.get("/pedido/<int:id_pedido>/ticket")
@login_required
@require_permission("pedidos.cobrar")
def ticket(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    return render_template("pos/ticket.html", pedido=pedido)


@bp.post("/pedido/<int:id_pedido>/cancelar")
@login_required
@require_permission("pedido.anular")
def cancelar(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    try:
        motivo = limpiar_texto(request.form.get("motivo"), 255)
        if not motivo:
            raise ValueError("Debe indicar motivo de cancelación.")
        cancelar_pedido(pedido, motivo)
        registrar_accion("Cancelar pedido", "POS", f"Pedido #{pedido.id_pedido}. Motivo: {motivo}")
        db.session.commit()
        flash("Pedido cancelado.", "warning")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("pos.index"))
