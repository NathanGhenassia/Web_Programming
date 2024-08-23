-- Crear base de datos
CREATE SCHEMA ERP;
USE ERP;

-- Crear tabla Clientes
CREATE TABLE Clientes (
    id VARCHAR(100) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(100) NOT NULL,
    segmento_negocio VARCHAR(100)
);

-- Crear tabla Productos
CREATE TABLE Productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(100),
    monto DECIMAL(10, 2) NOT NULL
);

-- Crear tabla Facturas
CREATE TABLE Facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id VARCHAR(100),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES Clientes(id)
);

-- Crear tabla DetallesFactura
CREATE TABLE DetallesFactura (
	id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT,
    producto_id INT,
    cantidad INT,
    FOREIGN KEY (factura_id) REFERENCES Facturas(id),
    FOREIGN KEY (producto_id) REFERENCES Productos(id)
);

-- Crear tabla Encuestas
CREATE TABLE Encuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id VARCHAR(100),
    factura_id INT,
    calificacion INT,
    comentario TEXT,
    FOREIGN KEY (cliente_id) REFERENCES Clientes(id),
    FOREIGN KEY (factura_id) REFERENCES Facturas(id)
);

INSERT INTO Productos (nombre, categoria, monto) VALUES
('Silla de comedor', 'Sillas', 120.00),
('Sofá modular', 'Sofás', 699.99),
('Escritorio ejecutivo', 'Escritorios', 350.50),
('Cama king-size', 'Camas', 899.00),
('Armario empotrado', 'Armarios', 450.75),
('Estantería de pared', 'Estanterías', 89.99),
('Lámpara de pie moderna', 'Lámparas', 129.95),
('Mesa de comedor de roble', 'Mesas', 299.50),
('Sillón reclinable', 'Sillones', 499.99),
('Mesa de centro de cristal', 'Mesas', 159.00),
('Cómoda de estilo vintage', 'Armarios', 279.95),
('Silla de oficina ergonómica', 'Sillas', 199.00),
('Sofá cama', 'Sofás', 599.00),
('Escritorio de esquina', 'Escritorios', 249.99),
('Cama individual con almacenaje', 'Camas', 349.50),
('Armario de puertas correderas', 'Armarios', 599.99),
('Estantería modular ajustable', 'Estanterías', 129.00),
('Lámpara colgante industrial', 'Lámparas', 79.95),
('Mesa de cocina extensible', 'Mesas', 199.50),
('Sillón de lectura', 'Sillones', 179.00),
('Mesita de noche con cajones', 'Mesas', 89.99),
('Sofá de tres plazas', 'Sofás', 799.00),
('Escritorio plegable', 'Escritorios', 149.50),
('Cama litera para niños', 'Camas', 399.00),
('Armario modular de bambú', 'Armarios', 229.95),
('Estantería flotante', 'Estanterías', 69.99),
('Lámpara de mesa vintage', 'Lámparas', 99.50),
('Mesa de centro con almacenaje', 'Mesas', 219.00),
('Silla de reuniones', 'Sillas', 149.00),
('Sofá de cuero genuino', 'Sofás', 1299.00),
('Escritorio para computadora', 'Escritorios', 179.50),
('Cama plegable de invitados', 'Camas', 129.95),
('Armario esquinero', 'Armarios', 399.99),
('Estantería de diseño minimalista', 'Estanterías', 149.00),
('Lámpara de techo ajustable', 'Lámparas', 119.95),
('Mesa alta de bar', 'Mesas', 149.50),
('Sillón giratorio', 'Sillones', 249.00),
('Cama nido con cajones', 'Camas', 299.99),
('Armario de almacenaje multiusos', 'Armarios', 179.00),
('Estante de esquina', 'Estanterías', 59.95),
('Camilla de hospital', 'Camas', 599.00),
('Escritorio médico', 'Escritorios', 249.99),
('Armario de suministros médicos', 'Armarios', 499.95),
('Lámpara de examen', 'Lámparas', 149.50),
('Pupitre de estudio', 'Escritorios', 149.00),
('Armario para libros', 'Armarios', 199.95),
('Casillero para bultos', 'Armarios', 129.99),
('Mostrador de recepción', 'Escritorios', 349.50),
('Armario de cocina', 'Armarios', 299.95),
('Lámpara colgante para restaurante', 'Lámparas', 129.50),
('Estantería de almacenaje de cocina', 'Estanterías', 149.00);