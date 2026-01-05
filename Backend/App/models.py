from .database import Base
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

class ConsultaClima(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    temperatura = Column(Float)
    descricao_climatica = Column(String)
    data_consulta = Column(DateTime, default=datetime.now)