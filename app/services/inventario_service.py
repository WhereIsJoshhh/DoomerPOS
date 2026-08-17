from decimal import Decimal
from datetime import datetime
from app.extensions import db
from app.models import Inventario, MovimientoInventario, Producto, Merma


def obtener_inventario_producto(id_producto: int, id_almacen: int | None = None):
    query = Inventario.query.filter_by(id_producto=id_producto)
    if id_almacen:
        query = query.filter_by(id_almacen=id_almacen)
    return query.first()


def hay_stock_suficiente(id_producto: int, cantidad: Decimal) -> bool:
    inventario = obtener_inventario_producto(id_producto)
    if not inventario:
        return False
    return Decimal(inventario.existencia_actual) >= Decimal(cantidad)


def registrar_movimiento(id_almacen: int, id_producto: int, id_usuario: int, tipo: str, cantidad: Decimal, motivo: str = ""):
    if tipo not in {"Entrada", "Salida", "Ajuste", "Venta", "Merma"}:
        raise ValueError("Tipo de movimiento de inventario no válido.")
    inventario = obtener_inventario_producto(id_producto, id_almacen)
    if not inventario:
        inventario = Inventario(id_almacen=id_almacen, id_producto=id_producto, existencia_actual=0, costo_promedio=0)
        db.session.add(inventario)
        db.session.flush()
    cantidad = Decimal(cantidad)
    if tipo in {"Entrada", "Ajuste"}:
        inventario.existencia_actual = Decimal(inventario.existencia_actual) + cantidad
    elif tipo in {"Salida", "Venta", "Merma"}:
        if Decimal(inventario.existencia_actual) < cantidad:
            raise ValueError("Stock insuficiente para realizar el movimiento.")
        inventario.existencia_actual = Decimal(inventario.existencia_actual) - cantidad
    inventario.actualizado_en = datetime.utcnow()
    movimiento = MovimientoInventario(
        id_almacen=id_almacen,
        id_producto=id_producto,
        id_usuario=id_usuario,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo,
    )
    db.session.add(movimiento)
    return movimiento


def descontar_por_venta(id_producto: int, cantidad: Decimal, id_usuario: int, motivo="Venta POS") -> None:
    inventario = obtener_inventario_producto(id_producto)
    if not inventario:
        raise ValueError("Producto sin inventario registrado.")
    registrar_movimiento(inventario.id_almacen, id_producto, id_usuario, "Venta", cantidad, motivo)


def registrar_merma(id_almacen: int, id_producto: int, id_usuario: int, cantidad: Decimal, motivo: str):
    registrar_movimiento(id_almacen, id_producto, id_usuario, "Merma", cantidad, motivo)
    merma = Merma(id_almacen=id_almacen, id_producto=id_producto, id_usuario=id_usuario, cantidad=cantidad, motivo=motivo)
    db.session.add(merma)
    return merma


def productos_bajo_stock():
    return (
        db.session.query(Inventario, Producto)
        .join(Producto, Producto.id_producto == Inventario.id_producto)
        .filter(Inventario.existencia_actual <= Producto.stock_minimo)
        .order_by(Inventario.existencia_actual.asc())
        .all()
    )
