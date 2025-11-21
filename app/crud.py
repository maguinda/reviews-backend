# app/crud.py
from __future__ import annotations

from sqlalchemy.orm import Session
from . import models
from .security import hash_password, verify_password


# ===================== USUARIOS =====================

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Obtiene un usuario por email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, password: str) -> models.User:
    """Crea un usuario nuevo con password hasheada."""
    user = models.User(
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    """
    Autentica un usuario:
    - Retorna el User si el password es correcto.
    - Retorna None si email o password no coinciden.
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ===================== RESEÑAS =====================

def create_review(
    db: Session,
    producto: str,
    texto_resena: str,
    sentimiento: str,
    usuario_email: str,
) -> models.Review:
    """
    Crea una reseña con sentimiento ya calculado.
    """
    review = models.Review(
        producto=producto,
        texto_resena=texto_resena,
        sentimiento=sentimiento,
        usuario_email=usuario_email,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews_by_product(db: Session, producto: str) -> list[models.Review]:
    """
    Obtiene todas las reseñas de un producto dado, ordenadas de la más reciente a la más antigua.
    """
    return (
        db.query(models.Review)
        .filter(models.Review.producto == producto)
        .order_by(models.Review.created_at.desc())
        .all()
    )
