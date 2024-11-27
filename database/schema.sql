-- Tabla de datos
CREATE TABLE IF NOT EXISTS datos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL DEFAULT 'AutoParkMX',
    direccion TEXT DEFAULT NULL,
    telefono TEXT DEFAULT NULL,
    horario TEXT DEFAULT NULL,
    recibo_pago BOOLEAN DEFAULT 1
);

-- Tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role_id INTEGER,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Tabla de tarifas (incluye tarifas horarias y de planes)
CREATE TABLE IF NOT EXISTS tarifas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,           -- Ej. "hora", "pension", "incidente"
    duracion TEXT,                -- Ej. "semanal", "mensual", "anual" (solo para pensiones)
    costo REAL NOT NULL
);

-- Tabla de tickets
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hora_entrada TEXT NOT NULL,
    hora_salida TEXT,
    total REAL,
    tarifa_name TEXT,
    tarifa_value REAL,
    corte TEXT,
    impreso BOOLEAN DEFAULT 0,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de cortes
CREATE TABLE IF NOT EXISTS cortes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    monto_total REAL NOT NULL,
    fecha TEXT NOT NULL,
    c_salida TEXT NOT NULL,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- crea apertura --
CREATE TABLE IF NOT EXISTS aperturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    door_name TEXT,                 -- Nombre de la puerta
    metodo_entrada TEXT NOT NULL,   -- Metodo de entrada (Botón/Tarjeta)
    card_number TEXT,               -- Número de tarjeta
    card_status TEXT,               -- Estado de la tarjeta
    error_code TEXT,                -- Código de error
    fecha TEXT NOT NULL,         -- Fecha y hora de la apertura
    usuario_id INTEGER,             -- ID del usuario
    corte TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


-- Tabla de sesiones
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    hora TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    documento TEXT NOT NULL,
    folio_documento TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    telefono TEXT,
    direccion TEXT,
    placa TEXT NOT NULL,
    modelo TEXT,
    fecha_registro TEXT NOT NULL,
    fecha_actualizacion TEXT ,
    usuario_id INTEGER NOT NULL,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de tarjetas de cliente
CREATE TABLE IF NOT EXISTS tarjetas_cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    numero_tarjeta TEXT NOT NULL UNIQUE,
    tarjeta_hex TEXT NOT NULL UNIQUE,
    fecha TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


-- Tabla de planes contratados
CREATE TABLE IF NOT EXISTS planes_contratados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    tarifa_costo DECIMAL,
    tarifa_duracion TEXT,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    activo BOOLEAN DEFAULT 1,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


-- Tabla de ingresos
CREATE TABLE IF NOT EXISTS ingresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monto REAL NOT NULL,
    tipo TEXT NOT NULL,             -- Ej. "ticket" para pagos por hora o "plan" para pagos de planes
    referencia_id INTEGER,          -- ID del ticket o del plan_contratado
    referencia_tipo TEXT,           -- "ticket" o "plan"
    usuario_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    corte TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de egresos
CREATE TABLE IF NOT EXISTS egresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monto REAL NOT NULL,
    tipo TEXT NOT NULL,             -- Tipo de egreso: pago de servicio, proveedor, etc.
    descripcion TEXT,               -- Detalles opcionales
    usuario_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    corte TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX idx_clientes_activo ON clientes(activo);
CREATE INDEX idx_clientes_nombre ON clientes(nombre);
CREATE INDEX idx_clientes_email ON clientes(email);
CREATE INDEX idx_clientes_folio_documento ON clientes(folio_documento);

CREATE INDEX idx_planes_cliente_id ON planes_contratados(cliente_id);
CREATE INDEX idx_planes_activo ON planes_contratados(activo);

CREATE INDEX idx_tarjetas_cliente_id ON tarjetas_cliente(cliente_id);
CREATE INDEX idx_tarjetas_activo ON tarjetas_cliente(activo);


-- Insertar roles
INSERT INTO roles (name) VALUES ('admin'), ('supervisor'), ('operador');

-- Insertar datos iniciales en la tabla datos
INSERT INTO datos (nombre, direccion, telefono, horario)
VALUES ("AutoPark", "Calle sin numero Col. Nueva", "477123456", "9:00-20:00");

-- Insertar tarifas iniciales
INSERT INTO tarifas (nombre, tipo, duracion, costo) VALUES
    ('auto', 'hora', NULL, 10),
    ('ticket perdido', 'incidente', NULL, 100),
    ('semanal', 'pension', 'semanal', 400),
    ('mensual', 'pension', 'mensual', 1500),
    ('anual', 'pension', 'anual', 2500),
    ('renovacion tarjeta', 'renovacion', Null, 20);
