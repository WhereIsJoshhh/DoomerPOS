ROLE_PERMISSIONS = {
    "Administrador": [
        "dashboard.ver",
        "sistema.configurar",
        "usuarios.gestionar",
        "roles.gestionar",
        "pos.operar",
        "pedidos.ver",
        "pedidos.cobrar",
        "cocina.operar",
        "caja.ver",
        "caja.abrir",
        "caja.mover",
        "caja.cerrar",
        "descuento.aprobar",
        "pedido.anular",
        "precio.editar",
        "inventario.ver",
        "inventario.gestionar",
        "compras.gestionar",
        "proveedores.gestionar",
        "reportes.ver",
        "reportes.exportar",
        "auditoria.ver",
    ],
    "Gerencia": [
        "dashboard.ver",
        "caja.ver",
        "inventario.ver",
        "reportes.ver",
        "reportes.exportar",
    ],
    "Gerente/Supervisor": [
        "dashboard.ver",
        "caja.ver",
        "inventario.ver",
        "reportes.ver",
        "reportes.exportar",
    ],
    "Consulta": [
        "dashboard.ver",
        "caja.ver",
        "inventario.ver",
        "reportes.ver",
    ],
    "Cajero": [
        "dashboard.ver",
        "pos.operar",
        "pedidos.ver",
        "pedidos.cobrar",
        "caja.ver",
        "caja.abrir",
        "caja.mover",
        "caja.cerrar",
        "reportes.caja",
    ],
    "Mesero": [
        "pos.operar",
        "pedidos.ver",
        "mesas.ver",
        "mesas.gestionar",
    ],
    "Cocina": [
        "cocina.operar",
        "pedidos.ver",
    ],
    "Cocina/Barra": [
        "cocina.operar",
        "pedidos.ver",
    ],
    "Inventario": [
        "inventario.ver",
        "inventario.gestionar",
        "compras.gestionar",
        "proveedores.gestionar",
    ],
    "Inventario/Almacén": [
        "inventario.ver",
        "inventario.gestionar",
        "compras.gestionar",
        "proveedores.gestionar",
    ],
}

PERMISSION_LABELS = {
    "dashboard.ver": "Ver dashboard",
    "sistema.configurar": "Configurar sistema",
    "usuarios.gestionar": "Gestionar usuarios",
    "roles.gestionar": "Gestionar roles",
    "pos.operar": "Operar POS",
    "pedidos.ver": "Ver pedidos",
    "pedidos.cobrar": "Cobrar pedidos",
    "mesas.ver": "Ver mesas",
    "mesas.gestionar": "Cambiar estado de mesas",
    "cocina.operar": "Gestionar cocina/KDS",
    "caja.ver": "Ver caja",
    "caja.abrir": "Abrir caja",
    "caja.mover": "Registrar movimientos de caja",
    "caja.cerrar": "Cerrar turno",
    "descuento.aprobar": "Aprobar descuentos",
    "pedido.anular": "Anular pedidos",
    "precio.editar": "Editar precios",
    "inventario.ver": "Ver inventario",
    "inventario.gestionar": "Gestionar inventario y mermas",
    "compras.gestionar": "Gestionar compras",
    "proveedores.gestionar": "Gestionar proveedores",
    "reportes.ver": "Ver reportes",
    "reportes.caja": "Ver reportes de caja",
    "reportes.exportar": "Exportar reportes",
    "auditoria.ver": "Ver bitácora",
}

MENU_ITEMS = [
    {"label": "Dashboard", "endpoint": "dashboard.index", "permission": "dashboard.ver", "icon": "Inicio"},
    {"label": "POS", "endpoint": "pos.index", "permission": "pos.operar", "icon": "Venta"},
    {"label": "Pedidos", "endpoint": "pos.index", "permission": "pedidos.ver", "icon": "Pedido"},
    {"label": "Mesas", "endpoint": "mesas.index", "permission": "mesas.ver", "icon": "Mesa"},
    {"label": "Cocina/KDS", "endpoint": "cocina.index", "permission": "cocina.operar", "icon": "KDS"},
    {"label": "Caja", "endpoint": "caja.index", "permission": "caja.ver", "icon": "Caja"},
    {"label": "Inventario", "endpoint": "inventario.index", "permission": "inventario.ver", "icon": "Stock"},
    {"label": "Compras", "endpoint": "compras.index", "permission": "compras.gestionar", "icon": "Compra"},
    {"label": "Proveedores", "endpoint": "compras.index", "permission": "proveedores.gestionar", "icon": "Prov"},
    {"label": "Productos", "endpoint": "productos.index", "permission": "inventario.gestionar", "icon": "Prod"},
    {"label": "Reportes", "endpoint": "reportes.index", "permission": "reportes.ver", "icon": "Rpt"},
    {"label": "Usuarios", "endpoint": "usuarios.index", "permission": "usuarios.gestionar", "icon": "Usr"},
    {"label": "Roles", "endpoint": "usuarios.index", "permission": "roles.gestionar", "icon": "Rol"},
    {"label": "Bitácora", "endpoint": "auditoria.index", "permission": "auditoria.ver", "icon": "Log"},
    {"label": "Configuración", "endpoint": "usuarios.index", "permission": "sistema.configurar", "icon": "Cfg"},
]


def permisos_para_rol(nombre_rol: str) -> list[str]:
    return ROLE_PERMISSIONS.get(nombre_rol or "", [])


def menu_para_usuario(usuario) -> list[dict]:
    if not usuario:
        return []
    return [item for item in MENU_ITEMS if usuario.puede(item["permission"])]


def primer_endpoint_permitido(usuario) -> str:
    menu = menu_para_usuario(usuario)
    return menu[0]["endpoint"] if menu else "auth.login"
