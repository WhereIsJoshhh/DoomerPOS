from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import CategoriaProducto, Producto, Almacen, Inventario
from app.utils.security import login_required, require_permission
from app.utils.validators import requerido, limpiar_texto, decimal_positivo, decimal_no_negativo
from app.services.auditoria_service import registrar_accion

bp = Blueprint("productos", __name__, url_prefix="/productos")


@bp.route("/")
@login_required
@require_permission("inventario.gestionar")
def index():
    q = request.args.get("q", "").strip()
    estado = request.args.get("estado", "")
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre).all()
    query = Producto.query
    if q:
        query = query.filter(Producto.nombre.ilike(f"%{q}%"))
    if estado:
        query = query.filter(Producto.estado == estado)
    productos = query.order_by(Producto.nombre).all()
    return render_template("productos/index.html", categorias=categorias, productos=productos, q=q, estado=estado)


@bp.post("/categoria")
@login_required
@require_permission("inventario.gestionar")
def categoria():
    try:
        nombre = requerido(request.form.get("nombre"), "nombre")
        descripcion = limpiar_texto(request.form.get("descripcion"), 255)
        db.session.add(CategoriaProducto(nombre=nombre, descripcion=descripcion))
        registrar_accion("Crear categoría", "Productos", nombre)
        db.session.commit()
        flash("Categoría creada.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("productos.index"))


@bp.post("/producto")
@login_required
@require_permission("inventario.gestionar")
def producto():
    try:
        id_categoria = int(request.form.get("id_categoria"))
        nombre = requerido(request.form.get("nombre"), "nombre")
        codigo = limpiar_texto(request.form.get("codigo"), 40) or None
        precio = decimal_positivo(request.form.get("precio"), "precio")
        costo = decimal_no_negativo(request.form.get("costo_estimado", "0"), "costo")
        stock_minimo = decimal_no_negativo(request.form.get("stock_minimo", "0"), "stock mínimo")
        descripcion = limpiar_texto(request.form.get("descripcion"), 255)
        producto = Producto(id_categoria=id_categoria, codigo=codigo, nombre=nombre, precio=precio, costo_estimado=costo, stock_minimo=stock_minimo, descripcion=descripcion)
        db.session.add(producto)
        db.session.flush()
        almacen = Almacen.query.filter_by(id_sucursal=g.usuario.id_sucursal).first()
        if almacen:
            db.session.add(Inventario(id_almacen=almacen.id_almacen, id_producto=producto.id_producto, existencia_actual=0, costo_promedio=costo))
        registrar_accion("Crear producto", "Productos", nombre)
        db.session.commit()
        flash("Producto creado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("productos.index"))


@bp.post("/producto/<int:id_producto>/estado")
@login_required
@require_permission("inventario.gestionar")
def cambiar_estado(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    producto.estado = "Inactivo" if producto.estado == "Activo" else "Activo"
    registrar_accion("Cambiar estado producto", "Productos", f"{producto.nombre}: {producto.estado}")
    db.session.commit()
    flash("Estado de producto actualizado.", "success")
    return redirect(url_for("productos.index"))
