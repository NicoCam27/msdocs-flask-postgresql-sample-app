from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import validates

from app import db

class Imagen(db.Model):
    __tablename__ = 'imagen'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(500)) #Nombre de Usuario
    nombre_archivo = Column(String(500)) #Nombre del Archivo
    n_pixeles_total = Column(Integer) #Nº Pixeles extraidos
    tipo_transformacion = Column(String(50)) #Tipo de transformacion - Copia, Blanco y Negro, Pixelado, Identificacion de Colores
    n_pixeles_azules = Column(Integer) #Nº Pixeles Azules
    n_pixeles_verdes = Column(Integer) #Nº Pixeles Verdes
    n_pixeles_rojos = Column(Integer) #Nº Pixeles Rojos
    fecha = Column(DateTime) #Fecha y Hora

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"