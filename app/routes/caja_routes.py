from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.extensions import db
from app.models import Terminal, Turno, MovimientoCaja, CierreCaja
from app.utils.security import login_required, require_permission
from app.utils.validators import decimal_no_negativo, decimal_positivo, limpiar_texto
from app.services.caja_service import obtener_turno_activo, abrir_turno, registrar_movimiento_caja, resumen_turno, cerrar_turno
from app.services.auditoria_service import registrar_accion

bp = Blueprint("caja", __name__, url_prefix="/caja")

@bp.route("/")
@login_required
@require_permission("caja.ver")
def index():
    turno = obtener_turno_activo(g.usuario.id_usuario)
    terminales = Terminal.query.filter_by(id_sucursal=g.usuario.id_sucursal, estado="Activa").all()
    movimientos = MovimientoCaja.query.filter_by(id_turno=turno.id_turno).order_by(MovimientoCaja.fecha.desc()).all() if turno else []
    cierres = CierreCaja.query.order_by(CierreCaja.fecha.desc()).limit(15).all()
    resumen = resumen_turno(turno)
    return render_template("caja/index.html", turno=turno, terminales=terminales, movimientos=movimientos, resumen=resumen, cierres=cierres)

@bp.post("/abrir")
@login_required
@require_permission("caja.abrir")
def abrir():
    try:
        id_terminal = request.form.get("id_terminal") or None
        fondo = decimal_no_negativo(request.form.get("fondo_inicial", "0"), "fondo inicial")
        observacion = limpiar_texto(request.form.get("observacion"), 255)
        turno = abrir_turno(g.usuario.id_usuario, int(id_terminal) if id_terminal else None, fondo, observacion)
        registrar_accion("Abrir turno", "Caja", f"Turno #{turno.id_turno}, fondo L {fondo}")
        db.session.commit()
        flash("Turno abierto correctamente.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("caja.index"))

@bp.post("/movimiento")
@login_required
@require_permission("caja.mover")
def movimiento():
    turno = obtener_turno_activo(g.usuario.id_usuario)
    if not turno:
        flash("No tienes turno abierto.", "warning")
        return redirect(url_for("caja.index"))
    try:
        tipo = request.form.get("tipo")
        concepto = limpiar_texto(request.form.get("concepto"), 120)
        monto = decimal_positivo(request.form.get("monto"), "monto")
        observacion = limpiar_texto(request.form.get("observacion"), 255)
        registrar_movimiento_caja(turno, g.usuario.id_usuario, tipo, concepto, monto, observacion)
        registrar_accion("Movimiento de caja", "Caja", f"{tipo}: {concepto} L {monto}")
        db.session.commit()
        flash("Movimiento registrado.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("caja.index"))

@bp.post("/cerrar")
@login_required
@require_permission("caja.cerrar")
def cerrar():
    turno = obtener_turno_activo(g.usuario.id_usuario)
    if not turno:
        flash("No tienes turno abierto.", "warning")
        return redirect(url_for("caja.index"))
    try:
        total_contado = decimal_no_negativo(request.form.get("total_contado", "0"), "total contado")
        observacion = limpiar_texto(request.form.get("observacion"), 255)
        cierre = cerrar_turno(turno, g.usuario.id_usuario, total_contado, observacion)
        registrar_accion("Cerrar turno", "Caja", f"Turno #{turno.id_turno}, diferencia L {cierre.diferencia}")
        db.session.commit()
        flash("Turno cerrado correctamente.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("caja.index"))
