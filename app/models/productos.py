from app.extensions import db

class CategoriaProducto(db.Model):
    __tablename__ = "categoria_producto"
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    descripcion = db.Column(db.String(255))

    productos = db.relationship("Producto", back_populates="categoria")

class Producto(db.Model):
    __tablename__ = "producto"
    id_producto = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(40), unique=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria_producto.id_categoria"), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    costo_estimado = db.Column(db.Numeric(10, 2), default=0)
    stock_minimo = db.Column(db.Numeric(10, 2), default=5)
    estado = db.Column(db.String(20), default="Activo")
    es_preparado = db.Column(db.Boolean, default=True)
    tiempo_preparacion_min = db.Column(db.Integer, default=10)
    descripcion = db.Column(db.String(255))

    categoria = db.relationship("CategoriaProducto", back_populates="productos")
    modificadores = db.relationship("Modificador", back_populates="producto", cascade="all, delete-orphan")
    recetas = db.relationship("Receta", back_populates="producto", cascade="all, delete-orphan")
    inventarios = db.relationship("Inventario", back_populates="producto")
    detalles_pedido = db.relationship("DetallePedido", back_populates="producto")
    mermas = db.relationship("Merma", back_populates="producto")

class Modificador(db.Model):
    __tablename__ = "modificador"
    id_modificador = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    precio_extra = db.Column(db.Numeric(10, 2), default=0)

    producto = db.relationship("Producto", back_populates="modificadores")

class Ingrediente(db.Model):
    __tablename__ = "ingrediente"
    id_ingrediente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    unidad_medida = db.Column(db.String(30), nullable=False)
    stock_minimo = db.Column(db.Numeric(10, 2), default=0)

    recetas = db.relationship("Receta", back_populates="ingrediente")

class Receta(db.Model):
    __tablename__ = "receta"
    id_receta = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey("producto.id_producto"), nullable=False)
    id_ingrediente = db.Column(db.Integer, db.ForeignKey("ingrediente.id_ingrediente"), nullable=False)
    cantidad_requerida = db.Column(db.Numeric(10, 3), nullable=False)

    producto = db.relationship("Producto", back_populates="recetas")
    ingrediente = db.relationship("Ingrediente", back_populates="recetas")
