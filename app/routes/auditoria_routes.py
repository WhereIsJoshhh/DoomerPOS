from flask import Blueprint, render_template, request
from app.models import AuditoriaLog, Usuario
from app.utils.security import login_required, require_permission

bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")

@bp.route("/")
@login_required
@require_permission("auditoria.ver")
def index():
    usuario_id = request.args.get("usuario_id")
    modulo = request.args.get("modulo", "").strip()
    query = AuditoriaLog.query
    if usuario_id:
        query = query.filter(AuditoriaLog.id_usuario == int(usuario_id))
    if modulo:
        query = query.filter(AuditoriaLog.modulo.ilike(f"%{modulo}%"))
    logs = query.order_by(AuditoriaLog.fecha_hora.desc()).limit(200).all()
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template("auditoria/index.html", logs=logs, usuarios=usuarios, usuario_id=usuario_id, modulo=modulo)
