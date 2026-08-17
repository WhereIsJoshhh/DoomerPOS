# Arquitectura de DoomerPOS v4.0

DoomerPOS v4.0 está organizado en capas para facilitar mantenimiento, escalabilidad y explicación académica.

## Capas principales

1. **Presentación:** plantillas HTML/Jinja2, CSS responsive y JavaScript básico.
2. **Rutas:** blueprints por módulo: auth, dashboard, POS, mesas, cocina, caja, inventario, compras, reportes, usuarios y auditoría.
3. **Servicios:** reglas de negocio reutilizables para pedidos, caja, inventario y auditoría.
4. **Modelos:** entidades SQLAlchemy por dominio.
5. **Datos:** SQLite para pruebas académicas; el diseño permite migrar a PostgreSQL.

## Decisiones de diseño

- Los pedidos tienen estados claros para reflejar el flujo real del restaurante.
- Las mesas usan estados visuales para facilitar atención en salón.
- Caja separa turno, pagos, movimientos y cierre.
- Inventario registra movimientos para trazabilidad.
- Compras actualizan stock y conservan historial de proveedor.
- Auditoría registra acciones críticas.

## Preparación futura

El proyecto puede crecer hacia API REST, facturación fiscal autorizada, integración bancaria, delivery, impresión real de tickets, reportes PDF/Excel y despliegue con Docker/PostgreSQL.
