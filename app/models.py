from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Relación con reseñas
    reviews = relationship("Review", back_populates="author")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    # Nombre EXACTO que usas en crud.py
    producto = Column(String(255), index=True, nullable=False)
    texto_resena = Column(Text, nullable=False)

    sentimiento = Column(String(20), nullable=False)  # positivo / negativo / neutro
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con usuario
    usuario_email = Column(String(255), ForeignKey("users.email"))
    author = relationship("User", back_populates="reviews")



