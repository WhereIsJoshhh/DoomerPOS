from decimal import Decimal
from datetime import datetime
from sqlalchemy import func
from app.extensions import db
from app.models import Turno, Pago, MetodoPago, MovimientoCaja, CierreCaja


def obtener_turno_activo(id_usuario: int):
    return Turno.query.filter_by(id_usuario=id_usuario, estado="Abierto").order_by(Turno.fecha_apertura.desc()).first()


def abrir_turno(id_usuario: int, id_terminal: int | None, fondo_inicial: Decimal, observacion: str = ""):
    if obtener_turno_activo(id_usuario):
        raise ValueError("Ya tienes un turno abierto.")
    turno = Turno(id_usuario=id_usuario, id_terminal=id_terminal, fondo_inicial=fondo_inicial, observacion_apertura=observacion)
    db.session.add(turno)
    db.session.flush()
    return turno


def registrar_movimiento_caja(turno: Turno, id_usuario: int, tipo: str, concepto: str, monto: Decimal, observacion: str = ""):
    if tipo not in {"Ingreso", "Egreso"}:
        raise ValueError("Tipo de movimiento de caja no válido.")
    movimiento = MovimientoCaja(id_turno=turno.id_turno, id_usuario=id_usuario, tipo=tipo, concepto=concepto, monto=monto, observacion=observacion)
    db.session.add(movimiento)
    return movimiento


def resumen_turno(turno: Turno):
    if not turno:
        return {"efectivo": Decimal("0"), "tarjeta": Decimal("0"), "transferencia": Decimal("0"), "ingresos": Decimal("0"), "egresos": Decimal("0"), "total_sistema": Decimal("0")}
    pagos = (
        db.session.query(MetodoPago.nombre, func.coalesce(func.sum(Pago.monto), 0))
        .join(MetodoPago, MetodoPago.id_metodo_pago == Pago.id_metodo_pago)
        .filter(Pago.id_turno == turno.id_turno)
        .group_by(MetodoPago.nombre)
        .all()
    )
    valores = {nombre.lower(): Decimal(total) for nombre, total in pagos}
    ingresos = db.session.query(func.coalesce(func.sum(MovimientoCaja.monto), 0)).filter_by(id_turno=turno.id_turno, tipo="Ingreso").scalar() or Decimal("0")
    egresos = db.session.query(func.coalesce(func.sum(MovimientoCaja.monto), 0)).filter_by(id_turno=turno.id_turno, tipo="Egreso").scalar() or Decimal("0")
    efectivo = valores.get("efectivo", Decimal("0"))
    tarjeta = valores.get("tarjeta", Decimal("0"))
    transferencia = valores.get("transferencia", Decimal("0"))
    total_sistema = Decimal(turno.fondo_inicial or 0) + efectivo + Decimal(ingresos) - Decimal(egresos)
    return {"efectivo": efectivo, "tarjeta": tarjeta, "transferencia": transferencia, "ingresos": Decimal(ingresos), "egresos": Decimal(egresos), "total_sistema": total_sistema}


def cerrar_turno(turno: Turno, id_usuario: int, total_contado: Decimal, observacion: str = ""):
    if turno.estado != "Abierto":
        raise ValueError("El turno ya está cerrado.")
    resumen = resumen_turno(turno)
    diferencia = Decimal(total_contado) - Decimal(resumen["total_sistema"])
    cierre = CierreCaja(
        id_turno=turno.id_turno,
        id_usuario=id_usuario,
        total_efectivo=resumen["efectivo"],
        total_tarjeta=resumen["tarjeta"],
        total_transferencia=resumen["transferencia"],
        total_ingresos=resumen["ingresos"],
        total_egresos=resumen["egresos"],
        total_sistema=resumen["total_sistema"],
        total_contado=total_contado,
        diferencia=diferencia,
        observacion=observacion,
    )
    turno.estado = "Cerrado"
    turno.fecha_cierre = datetime.utcnow()
    db.session.add(cierre)
    return cierre
