# app/schemas.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ===================== AUTH =====================

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ===================== REVIEWS =====================

class ReviewCreate(BaseModel):
    producto: str = Field(..., min_length=1)
    texto_resena: str = Field(..., min_length=1)  # <-- SIN TILDE (coincide con models)


class ReviewOut(BaseModel):
    id: int
    producto: str
    texto_resena: str
    sentimiento: str
    created_at: datetime
    usuario_email: str   # <-- nombre del campo REAL en tu modelo

    class Config:
        from_attributes = True
