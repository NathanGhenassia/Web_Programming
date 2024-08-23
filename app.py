# Importar librerias
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, ForeignKey, DECIMAL, TIMESTAMP, func, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import URL
import requests

# Estilos y colores
st.set_page_config(layout="centered", page_icon="🪑", page_title="Mueblería Nara")
st.image("logo.jpg", width=300)

page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(90deg, rgba(176, 176, 176, 1), rgba(191, 203, 255, 1))
}
.stButton>button {
    background-color: #bfcbff;
    color: #000000;
}
.stButton>button:hover {
    background-color: #bfcbff;
}
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


# Conexion a la base de datos
url_object = URL.create(
    "mysql+mysqlconnector",
    username="root",
    password="123Queso.",
    host="localhost",
    database="ERP",
    port=3306
)

engine = create_engine(url_object, echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# Clases que relacionan las tablas de mySQL
class Clientes(Base):
    __tablename__ = 'Clientes'
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    segmento_negocio = Column(String(100))

class Productos(Base):
    __tablename__ = 'Productos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(100))
    monto = Column(DECIMAL(10, 2), nullable=False)

class Facturas(Base):
    __tablename__ = 'Facturas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('Clientes.id'))
    fecha = Column(TIMESTAMP, server_default=func.now())
    cliente = relationship("Clientes", backref="facturas")

class DetallesFactura(Base):
    __tablename__ = 'DetallesFactura'
    id = Column(Integer, primary_key=True, autoincrement=True)
    factura_id = Column(Integer, ForeignKey('Facturas.id'))
    producto_id = Column(Integer, ForeignKey('Productos.id'))
    cantidad = Column(Integer)
    factura = relationship("Facturas", backref="detalles")
    producto = relationship("Productos", backref="detalles")

class Encuestas(Base):
    __tablename__ = 'Encuestas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(BigInteger, ForeignKey('Clientes.id'))
    factura_id = Column(Integer, ForeignKey('Facturas.id'))
    calificacion = Column(Integer, nullable=False)
    comentario = Column(Text)
    cliente = relationship("Clientes", backref="encuestas")
    factura = relationship("Facturas", backref="encuestas")


# Funcion para generar un usuario
def formulario():
    st.subheader("Ingresar datos de usuario")
    id = st.text_input("Ingresar numero de identificacion")
    nombre = st.text_input("Ingresar nombre")
    apellido = st.text_input("Ingresar apellido")
    correo_electronico = st.text_input("Ingresar correo electronico")
    segmento_negocio = st.selectbox("Ingresar segmento de negocio", ["Hogares residenciales", "Oficinas y espacios comerciales", "Hoteles y hospedajes", "Restaurantes y cafeterías", "Instituciones educativas", "Centros de salud y hospitales", "Centros de eventos y conferencias"])
    if st.button("Crear usuario"):
        usuario_existente = session.query(Clientes).filter(Clientes.id == id).first()
        if usuario_existente:
            st.error("Error: El usuario con este ID ya existe.")
        else:
            nuevo_usuario = Clientes(id=id, nombre=nombre, apellido=apellido, correo_electronico=correo_electronico, segmento_negocio=segmento_negocio)
            session.add(nuevo_usuario)
            session.commit()
            st.success("Nuevo usuario creado con exito!")   


# Funcion para realizar compras
def compra():
    st.subheader("Realizar compra")
    cliente_id = st.text_input("Ingresar numero de identificacion del cliente", key="compra")
    productos = session.query(Productos).all()
    productos_dict = {producto.nombre: producto for producto in productos}
    selected_products = st.multiselect("Seleccionar productos", list(productos_dict.keys()))
    
    if selected_products:
        total = 0
        detalles = []
        for product_name in selected_products:
            producto = productos_dict[product_name]
            cantidad = st.number_input(f"Ingresar cantidad para {product_name}", min_value=1, step=1, key=product_name)
            st.write(f"Precio del producto {product_name}: ${producto.monto * cantidad:.2f}")
            total += producto.monto * cantidad
            detalles.append((producto, cantidad))
        
        st.write(f"Total: ${total:.2f}")
        
        if st.button("Agregar al carrito"):
            nueva_factura = Facturas(cliente_id=cliente_id)
            session.add(nueva_factura)
            session.commit()
            
            for producto, cantidad in detalles:
                detalle_factura = DetallesFactura(factura_id=nueva_factura.id, producto_id=producto.id, cantidad=cantidad)
                session.add(detalle_factura)
            
            session.commit()
            st.success(f"Productos agregados al carrito con exito! Total a pagar: ${total:.2f}")


# Funcion para ver todas las facturas
def carrito():
    st.subheader("Ver facturas")
    cliente_id = st.text_input("Ingresar numero de identificacion del cliente", key="carrito")
    if st.button("Mostrar facturas"):
        facturas = session.query(Facturas).filter(Facturas.cliente_id == cliente_id).all()
        if not facturas:
            st.warning("No se encontraron facturas para este cliente.")
        else:
            data = []
            for factura in facturas:
                cliente = session.query(Clientes).filter(Clientes.id == cliente_id).first()
                detalles = session.query(DetallesFactura).filter(DetallesFactura.factura_id == factura.id).all()
                for detalle in detalles:
                    producto = session.query(Productos).filter(Productos.id == detalle.producto_id).first()
                    total = producto.monto * detalle.cantidad
                    data.append({
                        'ID de Factura': factura.id,
                        'Nombre del Cliente': cliente.nombre,
                        'Apellido del Cliente': cliente.apellido,
                        'Nombre del Producto': producto.nombre,
                        'Categoría del Producto': producto.categoria,
                        'Monto del Producto': producto.monto,
                        'Cantidad': detalle.cantidad,
                        'Total de la Compra': total,
                        'Fecha de la Factura': factura.fecha
                    })
            df = pd.DataFrame(data)
            st.dataframe(df)


# Funcion para listar los clientes actuales
def lista_clientes():
    st.subheader("Lista de clientes")
    clientes = session.query(Clientes).all()
    data = []
    for cliente in clientes:
        facturas = session.query(Facturas).filter(Facturas.cliente_id == cliente.id).all()
        total_gastado = sum(factura.detalles[0].producto.monto * factura.detalles[0].cantidad for factura in facturas)
        data.append({
            'ID del Cliente': cliente.id,
            'Nombre': cliente.nombre,
            'Apellido': cliente.apellido,
            'Correo Electrónico': cliente.correo_electronico,
            'Segmento de Negocio': cliente.segmento_negocio,
            'Total Gastado': total_gastado
        })
    df = pd.DataFrame(data)
    st.dataframe(df)


# Funcion para formulario de encuesta
def encuesta():
    st.subheader("Encuesta de satisfacción")
    cliente_id = st.text_input("Ingresar número de identificación del cliente", key="encuesta_cliente")
    factura_id = st.text_input("Ingresar número de identificación de la factura", key="encuesta_factura")
    calificacion = st.selectbox("¿Qué tan satisfecho estás con tu compra?", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
    comentario = st.text_area("Deja un comentario si lo deseas:")
    
    if st.button("Enviar"):
        nueva_encuesta = Encuestas(
            cliente_id=cliente_id,
            factura_id=factura_id,
            calificacion=calificacion.count("⭐"),
            comentario=comentario
        )
        session.add(nueva_encuesta)
        session.commit()
        st.success("¡Gracias por tu feedback!")


# Funcion para el analisis de datos
def analitica():
    st.subheader("Analitica")

    # Call the FastAPI endpoint
    response = requests.get("http://localhost:8000/analitica")
    
    if response.status_code != 200:
        st.warning("No se encontraron encuestas.")
        return
    
    # Parse the JSON response
    result = response.json()
    
    df = pd.DataFrame(result['data'])
    st.dataframe(df)
    
    calificaciones = pd.Series(result['calificaciones'])
    fig1 = px.bar(calificaciones, x=calificaciones.index, y=calificaciones.values, 
                  labels={'x': 'Calificación', 'y': 'Cantidad'}, 
                  title='Distribución de Calificaciones de Encuestas',
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1)
    
    porcentajes = pd.DataFrame(list(result['porcentajes'].items()), columns=['Categoría', 'Porcentaje'])
    fig2 = px.pie(porcentajes, names='Categoría', values='Porcentaje', 
                  title='Porcentajes de Calificaciones Mayor a 3 y Menor o Igual a 3',
                  labels={'Porcentaje': 'Porcentaje'},
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig2.update_traces(textinfo='label+percent', pull=[0.1, 0.1])
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2)



# Funcion main para llamar las funciones para cada tab
def main():
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Crear usuario", "Realizar compra", "Ver facturas", "Mis clientes", "Encuesta de satisfacción", "Analitica"])

    with tab1:
        formulario()
    with tab2:
        compra()
    with tab3:
        carrito()
    with tab4:
        lista_clientes()
    with tab5:
        encuesta()
    with tab6:
        analitica()

if __name__ == "__main__":
    main()

# Run the app with: python -m streamlit run app.py