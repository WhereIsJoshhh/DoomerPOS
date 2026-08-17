from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import Producto, CategoriaProducto, Inventario, Almacen, MovimientoInventario, Merma
from app.utils.security import login_required, require_permission, require_any_permission
from app.utils.validators import decimal_positivo, limpiar_texto
from app.services.inventario_service import registrar_movimiento, registrar_merma, productos_bajo_stock
from app.services.auditoria_service import registrar_accion

bp = Blueprint("inventario", __name__, url_prefix="/inventario")

@bp.route("/")
@login_required
@require_any_permission("inventario.ver", "inventario.gestionar")
def index():
    q = request.args.get("q", "").strip()
    inv_query = Inventario.query.join(Producto)
    if q:
        inv_query = inv_query.filter(Producto.nombre.ilike(f"%{q}%"))
    inventarios = inv_query.order_by(Inventario.existencia_actual.asc()).all()
    almacenes = Almacen.query.all()
    productos = Producto.query.order_by(Producto.nombre).all()
    movimientos = MovimientoInventario.query.order_by(MovimientoInventario.fecha.desc()).limit(20).all()
    mermas = Merma.query.order_by(Merma.fecha.desc()).limit(10).all()
    alertas = productos_bajo_stock()
    return render_template("inventario/index.html", inventarios=inventarios, almacenes=almacenes, productos=productos, movimientos=movimientos, mermas=mermas, alertas=alertas, q=q)

@bp.post("/movimiento")
@login_required
@require_permission("inventario.gestionar")
def movimiento():
    try:
        id_almacen = int(request.form.get("id_almacen"))
        id_producto = int(request.form.get("id_producto"))
        tipo = request.form.get("tipo")
        cantidad = decimal_positivo(request.form.get("cantidad"), "cantidad")
        motivo = limpiar_texto(request.form.get("motivo"), 255)
        if not motivo:
            raise ValueError("Debe ingresar un motivo.")
        registrar_movimiento(id_almacen, id_producto, g.usuario.id_usuario, tipo, cantidad, motivo)
        registrar_accion("Movimiento inventario", "Inventario", f"{tipo} producto {id_producto}, cantidad {cantidad}. {motivo}")
        db.session.commit()
        flash("Movimiento de inventario registrado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("inventario.index"))

@bp.post("/merma")
@login_required
@require_permission("inventario.gestionar")
def merma():
    try:
        id_almacen = int(request.form.get("id_almacen"))
        id_producto = int(request.form.get("id_producto"))
        cantidad = decimal_positivo(request.form.get("cantidad"), "cantidad")
        motivo = limpiar_texto(request.form.get("motivo"), 255)
        if not motivo:
            raise ValueError("Debe indicar motivo de la merma.")
        registrar_merma(id_almacen, id_producto, g.usuario.id_usuario, cantidad, motivo)
        registrar_accion("Registrar merma", "Inventario", f"Producto {id_producto}, cantidad {cantidad}. {motivo}")
        db.session.commit()
        flash("Merma registrada y stock actualizado.", "warning")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("inventario.index"))
