-- Schema DoomerPOS v4.0
-- Generado desde modelos SQLAlchemy

CREATE TABLE canal_venta (
	id_canal INTEGER NOT NULL, 
	nombre VARCHAR(80) NOT NULL, 
	descripcion VARCHAR(255), 
	PRIMARY KEY (id_canal), 
	UNIQUE (nombre)
);

CREATE TABLE categoria_producto (
	id_categoria INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	descripcion VARCHAR(255), 
	PRIMARY KEY (id_categoria), 
	UNIQUE (nombre)
);

CREATE TABLE cliente (
	id_cliente INTEGER NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	telefono VARCHAR(30), 
	correo VARCHAR(120), 
	estado VARCHAR(20), 
	PRIMARY KEY (id_cliente)
);

CREATE TABLE impuesto (
	id_impuesto INTEGER NOT NULL, 
	nombre VARCHAR(80) NOT NULL, 
	porcentaje NUMERIC(5, 2) NOT NULL, 
	PRIMARY KEY (id_impuesto)
);

CREATE TABLE ingrediente (
	id_ingrediente INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	unidad_medida VARCHAR(30) NOT NULL, 
	stock_minimo NUMERIC(10, 2), 
	PRIMARY KEY (id_ingrediente), 
	UNIQUE (nombre)
);

CREATE TABLE metodo_pago (
	id_metodo_pago INTEGER NOT NULL, 
	nombre VARCHAR(80) NOT NULL, 
	descripcion VARCHAR(255), 
	PRIMARY KEY (id_metodo_pago), 
	UNIQUE (nombre)
);

CREATE TABLE permiso (
	id_permiso INTEGER NOT NULL, 
	codigo VARCHAR(120) NOT NULL, 
	descripcion VARCHAR(255), 
	PRIMARY KEY (id_permiso), 
	UNIQUE (codigo)
);

CREATE TABLE proveedor (
	id_proveedor INTEGER NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	telefono VARCHAR(30), 
	correo VARCHAR(120), 
	contacto VARCHAR(120), 
	estado VARCHAR(20), 
	PRIMARY KEY (id_proveedor)
);

CREATE TABLE rol (
	id_rol INTEGER NOT NULL, 
	nombre VARCHAR(80) NOT NULL, 
	descripcion VARCHAR(255), 
	estado VARCHAR(20), 
	PRIMARY KEY (id_rol), 
	UNIQUE (nombre)
);

CREATE TABLE sucursal (
	id_sucursal INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	direccion VARCHAR(255), 
	telefono VARCHAR(30), 
	estado VARCHAR(20), 
	PRIMARY KEY (id_sucursal)
);

CREATE TABLE almacen (
	id_almacen INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	ubicacion VARCHAR(255), 
	PRIMARY KEY (id_almacen), 
	FOREIGN KEY(id_sucursal) REFERENCES sucursal (id_sucursal)
);

CREATE TABLE mesa (
	id_mesa INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	numero_mesa VARCHAR(20) NOT NULL, 
	zona VARCHAR(80), 
	capacidad INTEGER, 
	estado VARCHAR(20), 
	notas VARCHAR(255), 
	actualizado_en DATETIME, 
	PRIMARY KEY (id_mesa), 
	FOREIGN KEY(id_sucursal) REFERENCES sucursal (id_sucursal)
);

CREATE TABLE producto (
	id_producto INTEGER NOT NULL, 
	codigo VARCHAR(40), 
	id_categoria INTEGER NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	precio NUMERIC(10, 2) NOT NULL, 
	costo_estimado NUMERIC(10, 2), 
	stock_minimo NUMERIC(10, 2), 
	estado VARCHAR(20), 
	es_preparado BOOLEAN, 
	tiempo_preparacion_min INTEGER, 
	descripcion VARCHAR(255), 
	PRIMARY KEY (id_producto), 
	UNIQUE (codigo), 
	FOREIGN KEY(id_categoria) REFERENCES categoria_producto (id_categoria)
);

CREATE TABLE rol_permiso (
	id_rol_permiso INTEGER NOT NULL, 
	id_rol INTEGER NOT NULL, 
	id_permiso INTEGER NOT NULL, 
	PRIMARY KEY (id_rol_permiso), 
	CONSTRAINT uq_rol_permiso UNIQUE (id_rol, id_permiso), 
	FOREIGN KEY(id_rol) REFERENCES rol (id_rol), 
	FOREIGN KEY(id_permiso) REFERENCES permiso (id_permiso)
);

CREATE TABLE terminal (
	id_terminal INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	codigo_terminal VARCHAR(50) NOT NULL, 
	tipo VARCHAR(50), 
	estado VARCHAR(20), 
	PRIMARY KEY (id_terminal), 
	FOREIGN KEY(id_sucursal) REFERENCES sucursal (id_sucursal)
);

CREATE TABLE usuario (
	id_usuario INTEGER NOT NULL, 
	id_rol INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	nombre VARCHAR(120) NOT NULL, 
	usuario_login VARCHAR(80) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	estado VARCHAR(20), 
	intentos_fallidos INTEGER, 
	bloqueado_hasta DATETIME, 
	ultimo_acceso DATETIME, 
	creado_en DATETIME, 
	PRIMARY KEY (id_usuario), 
	FOREIGN KEY(id_rol) REFERENCES rol (id_rol), 
	FOREIGN KEY(id_sucursal) REFERENCES sucursal (id_sucursal), 
	UNIQUE (usuario_login)
);

CREATE TABLE auditoria_log (
	id_log INTEGER NOT NULL, 
	id_usuario INTEGER, 
	accion VARCHAR(120) NOT NULL, 
	modulo VARCHAR(80) NOT NULL, 
	fecha_hora DATETIME, 
	detalle TEXT, 
	ip VARCHAR(45), 
	user_agent VARCHAR(255), 
	PRIMARY KEY (id_log), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE autorizacion (
	id_autorizacion INTEGER NOT NULL, 
	tipo VARCHAR(40) NOT NULL, 
	id_usuario_solicita INTEGER NOT NULL, 
	id_usuario_autoriza INTEGER, 
	motivo VARCHAR(255) NOT NULL, 
	fecha DATETIME, 
	estado VARCHAR(20), 
	PRIMARY KEY (id_autorizacion), 
	FOREIGN KEY(id_usuario_solicita) REFERENCES usuario (id_usuario), 
	FOREIGN KEY(id_usuario_autoriza) REFERENCES usuario (id_usuario)
);

CREATE TABLE compra (
	id_compra INTEGER NOT NULL, 
	id_proveedor INTEGER NOT NULL, 
	id_almacen INTEGER NOT NULL, 
	fecha DATETIME, 
	total_compra NUMERIC(10, 2), 
	estado VARCHAR(20), 
	observacion VARCHAR(255), 
	PRIMARY KEY (id_compra), 
	FOREIGN KEY(id_proveedor) REFERENCES proveedor (id_proveedor), 
	FOREIGN KEY(id_almacen) REFERENCES almacen (id_almacen)
);

CREATE TABLE inventario (
	id_inventario INTEGER NOT NULL, 
	id_almacen INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	existencia_actual NUMERIC(10, 2), 
	costo_promedio NUMERIC(10, 2), 
	actualizado_en DATETIME, 
	PRIMARY KEY (id_inventario), 
	CONSTRAINT uq_inventario_almacen_producto UNIQUE (id_almacen, id_producto), 
	FOREIGN KEY(id_almacen) REFERENCES almacen (id_almacen), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto)
);

CREATE TABLE merma (
	id_merma INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	id_almacen INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	cantidad NUMERIC(10, 2) NOT NULL, 
	motivo VARCHAR(255) NOT NULL, 
	fecha DATETIME, 
	PRIMARY KEY (id_merma), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto), 
	FOREIGN KEY(id_almacen) REFERENCES almacen (id_almacen), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE modificador (
	id_modificador INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	precio_extra NUMERIC(10, 2), 
	PRIMARY KEY (id_modificador), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto)
);

CREATE TABLE movimiento_inventario (
	id_movimiento INTEGER NOT NULL, 
	id_almacen INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	tipo VARCHAR(30) NOT NULL, 
	cantidad NUMERIC(10, 2) NOT NULL, 
	motivo VARCHAR(255), 
	fecha DATETIME, 
	PRIMARY KEY (id_movimiento), 
	FOREIGN KEY(id_almacen) REFERENCES almacen (id_almacen), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE receta (
	id_receta INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	id_ingrediente INTEGER NOT NULL, 
	cantidad_requerida NUMERIC(10, 3) NOT NULL, 
	PRIMARY KEY (id_receta), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto), 
	FOREIGN KEY(id_ingrediente) REFERENCES ingrediente (id_ingrediente)
);

CREATE TABLE reserva (
	id_reserva INTEGER NOT NULL, 
	id_cliente INTEGER NOT NULL, 
	id_mesa INTEGER, 
	fecha_reserva DATETIME NOT NULL, 
	personas INTEGER, 
	estado VARCHAR(20), 
	notas VARCHAR(255), 
	creado_en DATETIME, 
	PRIMARY KEY (id_reserva), 
	FOREIGN KEY(id_cliente) REFERENCES cliente (id_cliente), 
	FOREIGN KEY(id_mesa) REFERENCES mesa (id_mesa)
);

CREATE TABLE turno (
	id_turno INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	id_terminal INTEGER, 
	fecha_apertura DATETIME, 
	fecha_cierre DATETIME, 
	fondo_inicial NUMERIC(10, 2), 
	estado VARCHAR(20), 
	observacion_apertura VARCHAR(255), 
	PRIMARY KEY (id_turno), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario), 
	FOREIGN KEY(id_terminal) REFERENCES terminal (id_terminal)
);

CREATE TABLE cierre_caja (
	id_cierre INTEGER NOT NULL, 
	id_turno INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	total_efectivo NUMERIC(10, 2), 
	total_tarjeta NUMERIC(10, 2), 
	total_transferencia NUMERIC(10, 2), 
	total_ingresos NUMERIC(10, 2), 
	total_egresos NUMERIC(10, 2), 
	total_sistema NUMERIC(10, 2), 
	total_contado NUMERIC(10, 2), 
	diferencia NUMERIC(10, 2), 
	observacion VARCHAR(255), 
	fecha DATETIME, 
	PRIMARY KEY (id_cierre), 
	FOREIGN KEY(id_turno) REFERENCES turno (id_turno), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE detalle_compra (
	id_detalle_compra INTEGER NOT NULL, 
	id_compra INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	cantidad NUMERIC(10, 2) NOT NULL, 
	costo_unitario NUMERIC(10, 2) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id_detalle_compra), 
	FOREIGN KEY(id_compra) REFERENCES compra (id_compra), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto)
);

CREATE TABLE movimiento_caja (
	id_movimiento_caja INTEGER NOT NULL, 
	id_turno INTEGER NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	tipo VARCHAR(20) NOT NULL, 
	concepto VARCHAR(120) NOT NULL, 
	monto NUMERIC(10, 2) NOT NULL, 
	fecha DATETIME, 
	observacion VARCHAR(255), 
	PRIMARY KEY (id_movimiento_caja), 
	FOREIGN KEY(id_turno) REFERENCES turno (id_turno), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE pedido (
	id_pedido INTEGER NOT NULL, 
	id_cliente INTEGER, 
	id_mesa INTEGER, 
	id_usuario INTEGER NOT NULL, 
	id_sucursal INTEGER NOT NULL, 
	id_canal INTEGER NOT NULL, 
	id_turno INTEGER, 
	fecha DATETIME, 
	fecha_cierre DATETIME, 
	estado VARCHAR(30), 
	prioridad VARCHAR(20), 
	subtotal NUMERIC(10, 2), 
	descuento NUMERIC(10, 2), 
	cargo_adicional NUMERIC(10, 2), 
	impuesto NUMERIC(10, 2), 
	total NUMERIC(10, 2), 
	tipo_pago VARCHAR(30), 
	descuento_motivo VARCHAR(255), 
	notas VARCHAR(255), 
	PRIMARY KEY (id_pedido), 
	FOREIGN KEY(id_cliente) REFERENCES cliente (id_cliente), 
	FOREIGN KEY(id_mesa) REFERENCES mesa (id_mesa), 
	FOREIGN KEY(id_usuario) REFERENCES usuario (id_usuario), 
	FOREIGN KEY(id_sucursal) REFERENCES sucursal (id_sucursal), 
	FOREIGN KEY(id_canal) REFERENCES canal_venta (id_canal), 
	FOREIGN KEY(id_turno) REFERENCES turno (id_turno)
);

CREATE TABLE detalle_pedido (
	id_detalle INTEGER NOT NULL, 
	id_pedido INTEGER NOT NULL, 
	id_producto INTEGER NOT NULL, 
	cantidad NUMERIC(10, 2) NOT NULL, 
	precio_unitario NUMERIC(10, 2) NOT NULL, 
	descuento NUMERIC(10, 2), 
	subtotal NUMERIC(10, 2) NOT NULL, 
	notas VARCHAR(255), 
	PRIMARY KEY (id_detalle), 
	FOREIGN KEY(id_pedido) REFERENCES pedido (id_pedido), 
	FOREIGN KEY(id_producto) REFERENCES producto (id_producto)
);

CREATE TABLE factura (
	id_factura INTEGER NOT NULL, 
	id_pedido INTEGER NOT NULL, 
	id_impuesto INTEGER NOT NULL, 
	numero_factura VARCHAR(80) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	descuento NUMERIC(10, 2), 
	cargo_adicional NUMERIC(10, 2), 
	impuesto_total NUMERIC(10, 2) NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	estado VARCHAR(20), 
	fecha DATETIME, 
	PRIMARY KEY (id_factura), 
	FOREIGN KEY(id_pedido) REFERENCES pedido (id_pedido), 
	FOREIGN KEY(id_impuesto) REFERENCES impuesto (id_impuesto), 
	UNIQUE (numero_factura)
);

CREATE TABLE pago (
	id_pago INTEGER NOT NULL, 
	id_pedido INTEGER NOT NULL, 
	id_metodo_pago INTEGER NOT NULL, 
	id_turno INTEGER, 
	monto NUMERIC(10, 2) NOT NULL, 
	fecha_pago DATETIME, 
	referencia VARCHAR(120), 
	PRIMARY KEY (id_pago), 
	FOREIGN KEY(id_pedido) REFERENCES pedido (id_pedido), 
	FOREIGN KEY(id_metodo_pago) REFERENCES metodo_pago (id_metodo_pago), 
	FOREIGN KEY(id_turno) REFERENCES turno (id_turno)
);