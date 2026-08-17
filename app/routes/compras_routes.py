from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import Proveedor, Compra, DetalleCompra, Almacen, Producto, Inventario
from app.utils.security import login_required, require_permission
from app.utils.validators import requerido, limpiar_texto, decimal_positivo, validar_email_opcional
from app.services.inventario_service import registrar_movimiento
from app.services.auditoria_service import registrar_accion

bp = Blueprint("compras", __name__, url_prefix="/compras")


@bp.route("/")
@login_required
@require_permission("compras.gestionar")
def index():
    q = request.args.get("q", "").strip()
    estado = request.args.get("estado", "")
    proveedores_query = Proveedor.query
    if q:
        proveedores_query = proveedores_query.filter(Proveedor.nombre.ilike(f"%{q}%"))
    if estado:
        proveedores_query = proveedores_query.filter(Proveedor.estado == estado)
    proveedores = proveedores_query.order_by(Proveedor.nombre).all()
    compras = Compra.query.order_by(Compra.fecha.desc()).limit(40).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    almacenes = Almacen.query.all()
    proveedores_activos = Proveedor.query.filter_by(estado="Activo").order_by(Proveedor.nombre).all()
    return render_template("compras/index.html", proveedores=proveedores, proveedores_activos=proveedores_activos, compras=compras, productos=productos, almacenes=almacenes, q=q, estado=estado)


@bp.post("/proveedor")
@login_required
@require_permission("compras.gestionar")
def nuevo_proveedor():
    try:
        proveedor = Proveedor(
            nombre=requerido(request.form.get("nombre"), "nombre"),
            telefono=limpiar_texto(request.form.get("telefono"), 30),
            correo=validar_email_opcional(request.form.get("correo")),
            contacto=limpiar_texto(request.form.get("contacto"), 120),
            estado=request.form.get("estado") or "Activo",
        )
        db.session.add(proveedor)
        registrar_accion("Crear proveedor", "Compras", proveedor.nombre)
        db.session.commit()
        flash("Proveedor creado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("compras.index"))


@bp.post("/proveedor/<int:id_proveedor>/estado")
@login_required
@require_permission("compras.gestionar")
def cambiar_estado_proveedor(id_proveedor):
    proveedor = Proveedor.query.get_or_404(id_proveedor)
    proveedor.estado = "Inactivo" if proveedor.estado == "Activo" else "Activo"
    registrar_accion("Cambiar estado proveedor", "Compras", f"{proveedor.nombre}: {proveedor.estado}")
    db.session.commit()
    flash("Estado de proveedor actualizado.", "success")
    return redirect(url_for("compras.index"))


@bp.post("/compra")
@login_required
@require_permission("compras.gestionar")
def nueva_compra():
    try:
        id_proveedor = int(request.form.get("id_proveedor"))
        proveedor = Proveedor.query.get_or_404(id_proveedor)
        if proveedor.estado != "Activo":
            raise ValueError("No se puede comprar a un proveedor inactivo.")
        id_almacen = int(request.form.get("id_almacen"))
        id_producto = int(request.form.get("id_producto"))
        cantidad = decimal_positivo(request.form.get("cantidad"), "cantidad")
        costo_unitario = decimal_positivo(request.form.get("costo_unitario"), "costo unitario")
        subtotal = (cantidad * costo_unitario).quantize(Decimal("0.01"))
        compra = Compra(id_proveedor=id_proveedor, id_almacen=id_almacen, total_compra=subtotal, observacion=limpiar_texto(request.form.get("observacion"), 255))
        db.session.add(compra)
        db.session.flush()
        db.session.add(DetalleCompra(id_compra=compra.id_compra, id_producto=id_producto, cantidad=cantidad, costo_unitario=costo_unitario, subtotal=subtotal))
        inventario = Inventario.query.filter_by(id_almacen=id_almacen, id_producto=id_producto).first()
        if inventario:
            inventario.costo_promedio = costo_unitario
        registrar_movimiento(id_almacen, id_producto, g.usuario.id_usuario, "Entrada", cantidad, f"Compra #{compra.id_compra}")
        registrar_accion("Registrar compra", "Compras", f"Compra #{compra.id_compra}, total L {subtotal}")
        db.session.commit()
        flash("Compra registrada y stock actualizado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("compras.index"))
