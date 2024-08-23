from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, ForeignKey, DECIMAL, TIMESTAMP, func, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict
from sqlalchemy import URL
import uvicorn

DATABASE_URL = URL.create(
    "mysql+mysqlconnector",
    username="root",
    password="123Queso.",
    host="localhost",
    database="ERP",
    port=3306
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Clientes(Base):
    __tablename__ = 'Clientes'
    id = Column(BigInteger, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo_electronico = Column(String(100), nullable=False)
    segmento_negocio = Column(String(100))

class Facturas(Base):
    __tablename__ = 'Facturas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('Clientes.id'))
    fecha = Column(TIMESTAMP, server_default=func.now())
    cliente = relationship("Clientes", backref="facturas")

class Encuestas(Base):
    __tablename__ = 'Encuestas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(BigInteger, ForeignKey('Clientes.id'))
    factura_id = Column(Integer, ForeignKey('Facturas.id'))
    calificacion = Column(Integer, nullable=False)
    comentario = Column(Text)
    cliente = relationship("Clientes", backref="encuestas")
    factura = relationship("Facturas", backref="encuestas")

class AnaliticaResponse(BaseModel):
    data: List[Dict]
    calificaciones: Dict
    porcentajes: Dict

app = FastAPI()

@app.get("/analitica", response_model=AnaliticaResponse)
def get_analitica():
    session = SessionLocal()
    try:
        encuestas = session.query(Encuestas).all()
        if not encuestas:
            raise HTTPException(status_code=404, detail="No se encontraron encuestas.")
        
        data = []
        for encuesta in encuestas:
            cliente = session.query(Clientes).filter(Clientes.id == encuesta.cliente_id).first()
            factura = session.query(Facturas).filter(Facturas.id == encuesta.factura_id).first()
            data.append({
                'ID de Encuesta': encuesta.id,
                'Nombre del Cliente': cliente.nombre,
                'Apellido del Cliente': cliente.apellido,
                'Calificación': encuesta.calificacion,
                'Comentario': encuesta.comentario,
                'Fecha de la Factura': factura.fecha
            })
        
        df = pd.DataFrame(data)
        
        calificaciones = df['Calificación'].value_counts().sort_index().to_dict()
        
        calificaciones_mayor_3 = (df['Calificación'] > 3).sum()
        calificaciones_menor_igual_3 = (df['Calificación'] <= 3).sum()
        total_calificaciones = calificaciones_mayor_3 + calificaciones_menor_igual_3
        porcentaje_mayor_3 = (calificaciones_mayor_3 / total_calificaciones) * 100
        porcentaje_menor_igual_3 = (calificaciones_menor_igual_3 / total_calificaciones) * 100
        
        porcentajes = {
            'Mayor a 3': porcentaje_mayor_3,
            'Menor o igual a 3': porcentaje_menor_igual_3
        }
        
        return AnaliticaResponse(
            data=data,
            calificaciones=calificaciones,
            porcentajes=porcentajes
        )
    finally:
        session.close()

# Run the API with: python -m uvicorn main:app --reload
