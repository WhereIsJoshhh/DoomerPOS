from decimal import Decimal
from datetime import datetime
from app.extensions import db
from app.models import Pedido, DetallePedido, Producto, Impuesto, Factura, Pago, Mesa, MetodoPago
from app.services.inventario_service import descontar_por_venta, hay_stock_suficiente

ESTADOS_PEDIDO = ["pendiente", "en cocina", "listo", "servido", "pagado", "cancelado"]
TRANSICIONES_PEDIDO = {
    "pendiente": {"en cocina", "cancelado"},
    "en cocina": {"listo", "cancelado"},
    "listo": {"servido", "cancelado"},
    "servido": {"pagado", "cancelado"},
    "pagado": set(),
    "cancelado": set(),
}


def _money(valor) -> Decimal:
    return Decimal(valor or 0).quantize(Decimal("0.01"))


def recalcular_totales(pedido: Pedido) -> None:
    subtotal = sum(_money(d.subtotal) for d in pedido.detalles)
    descuento = min(_money(pedido.descuento), subtotal)
    cargo = _money(pedido.cargo_adicional)
    impuesto_default = Impuesto.query.first()
    tasa = Decimal(impuesto_default.porcentaje if impuesto_default else 0) / Decimal("100")
    base_imponible = max(Decimal("0.00"), subtotal - descuento + cargo)
    impuesto = (base_imponible * tasa).quantize(Decimal("0.01"))
    total = (base_imponible + impuesto).quantize(Decimal("0.01"))
    pedido.subtotal = subtotal
    pedido.descuento = descuento
    pedido.cargo_adicional = cargo
    pedido.impuesto = impuesto
    pedido.total = total


def crear_pedido(id_usuario: int, id_sucursal: int, id_canal: int, id_cliente=None, id_mesa=None, notas="", prioridad="normal"):
    pedido = Pedido(
        id_usuario=id_usuario,
        id_sucursal=id_sucursal,
        id_canal=id_canal,
        id_cliente=id_cliente,
        id_mesa=id_mesa,
        estado="pendiente",
        prioridad=prioridad if prioridad in {"normal", "alta"} else "normal",
        notas=notas,
    )
    if id_mesa:
        mesa = Mesa.query.get(id_mesa)
        if not mesa:
            raise ValueError("La mesa seleccionada no existe.")
        if mesa.estado not in {"libre", "reservada"}:
            raise ValueError("La mesa seleccionada no está disponible.")
        mesa.estado = "ocupada"
        mesa.actualizado_en = datetime.utcnow()
    db.session.add(pedido)
    db.session.flush()
    return pedido


def agregar_producto_a_pedido(pedido: Pedido, id_producto: int, cantidad: Decimal, notas="") -> DetallePedido:
    if pedido.estado in {"pagado", "cancelado"}:
        raise ValueError("No se puede modificar un pedido pagado o cancelado.")
    producto = Producto.query.get_or_404(id_producto)
    if producto.estado != "Activo":
        raise ValueError("No se puede vender un producto inactivo.")
    if not hay_stock_suficiente(producto.id_producto, cantidad):
        raise ValueError("Stock insuficiente para este producto.")
    subtotal = (Decimal(producto.precio) * Decimal(cantidad)).quantize(Decimal("0.01"))
    detalle = DetallePedido(pedido=pedido, id_producto=id_producto, cantidad=cantidad, precio_unitario=producto.precio, subtotal=subtotal, notas=notas)
    db.session.add(detalle)
    recalcular_totales(pedido)
    return detalle


def aplicar_ajustes_pedido(pedido: Pedido, descuento: Decimal = Decimal("0"), cargo_adicional: Decimal = Decimal("0"), motivo: str = "") -> None:
    if pedido.estado in {"pagado", "cancelado"}:
        raise ValueError("No se puede ajustar un pedido cerrado.")
    if descuento < 0 or cargo_adicional < 0:
        raise ValueError("Descuento y cargo adicional no pueden ser negativos.")
    pedido.descuento = descuento.quantize(Decimal("0.01"))
    pedido.cargo_adicional = cargo_adicional.quantize(Decimal("0.01"))
    pedido.descuento_motivo = motivo[:255] if motivo else None
    recalcular_totales(pedido)


def enviar_a_cocina(pedido: Pedido) -> None:
    if not pedido.detalles:
        raise ValueError("No se puede enviar a cocina un pedido sin productos.")
    if pedido.estado != "pendiente":
        raise ValueError("Solo los pedidos pendientes pueden enviarse a cocina.")
    pedido.estado = "en cocina"


def cambiar_estado_pedido(pedido: Pedido, estado: str) -> None:
    if estado not in ESTADOS_PEDIDO:
        raise ValueError("Estado de pedido no válido.")
    if pedido.estado in {"pagado", "cancelado"}:
        raise ValueError("No se puede cambiar el estado de un pedido cerrado.")
    permitidos = TRANSICIONES_PEDIDO.get(pedido.estado, set())
    if estado not in permitidos and estado != pedido.estado:
        raise ValueError(f"Transición no permitida: {pedido.estado} → {estado}.")
    pedido.estado = estado


def _cerrar_operacion_pagada(pedido: Pedido, id_usuario: int, id_turno: int | None, tipo_pago: str) -> None:
    for detalle in pedido.detalles:
        descontar_por_venta(detalle.id_producto, Decimal(detalle.cantidad), id_usuario, f"Pedido #{pedido.id_pedido}")
    pedido.estado = "pagado"
    pedido.fecha_cierre = datetime.utcnow()
    pedido.id_turno = id_turno
    pedido.tipo_pago = tipo_pago
    if pedido.mesa:
        pedido.mesa.estado = "limpieza"
        pedido.mesa.actualizado_en = datetime.utcnow()
    impuesto_default = Impuesto.query.first()
    if impuesto_default and not pedido.facturas:
        factura = Factura(
            id_pedido=pedido.id_pedido,
            id_impuesto=impuesto_default.id_impuesto,
            numero_factura=f"DPOS4-{pedido.id_pedido:06d}",
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            cargo_adicional=pedido.cargo_adicional,
            impuesto_total=pedido.impuesto,
            total=pedido.total,
        )
        db.session.add(factura)


def cobrar_pedido(pedido: Pedido, id_metodo_pago: int, monto: Decimal, id_usuario: int, id_turno: int | None, referencia: str = ""):
    if pedido.estado == "pagado":
        raise ValueError("El pedido ya fue pagado.")
    if pedido.estado == "cancelado":
        raise ValueError("No se puede cobrar un pedido cancelado.")
    if not pedido.detalles:
        raise ValueError("No se puede cobrar un pedido sin productos.")
    monto = Decimal(monto).quantize(Decimal("0.01"))
    if monto < Decimal(pedido.total):
        raise ValueError("El monto recibido no puede ser menor al total del pedido.")
    metodo = MetodoPago.query.get_or_404(id_metodo_pago)
    pago = Pago(id_pedido=pedido.id_pedido, id_metodo_pago=id_metodo_pago, id_turno=id_turno, monto=pedido.total, referencia=referencia)
    db.session.add(pago)
    _cerrar_operacion_pagada(pedido, id_usuario, id_turno, metodo.nombre)
    return pago


def cobrar_pedido_mixto(pedido: Pedido, pagos: dict[str, Decimal], id_usuario: int, id_turno: int | None, referencia: str = ""):
    if pedido.estado in {"pagado", "cancelado"}:
        raise ValueError("No se puede cobrar un pedido cerrado o cancelado.")
    if not pedido.detalles:
        raise ValueError("No se puede cobrar un pedido sin productos.")
    total_pagado = sum((Decimal(monto) for monto in pagos.values()), Decimal("0.00")).quantize(Decimal("0.01"))
    if total_pagado != Decimal(pedido.total).quantize(Decimal("0.01")):
        raise ValueError("En pago mixto, la suma de métodos debe ser igual al total exacto del pedido.")
    creados = []
    for nombre, monto in pagos.items():
        monto = Decimal(monto).quantize(Decimal("0.01"))
        if monto <= 0:
            continue
        metodo = MetodoPago.query.filter_by(nombre=nombre).first()
        if not metodo:
            raise ValueError(f"No existe el método de pago {nombre}.")
        pago = Pago(id_pedido=pedido.id_pedido, id_metodo_pago=metodo.id_metodo_pago, id_turno=id_turno, monto=monto, referencia=referencia or "Pago mixto")
        db.session.add(pago)
        creados.append(pago)
    _cerrar_operacion_pagada(pedido, id_usuario, id_turno, "Mixto")
    return creados


def cancelar_pedido(pedido: Pedido, motivo="") -> None:
    if pedido.estado == "pagado":
        raise ValueError("No se puede cancelar un pedido pagado.")
    pedido.estado = "cancelado"
    pedido.notas = ((pedido.notas or "") + f" | Cancelado: {motivo}").strip()
    if pedido.mesa:
        pedido.mesa.estado = "libre"
        pedido.mesa.actualizado_en = datetime.utcnow()
