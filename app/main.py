# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from . import models, schemas, crud, gemini_client
from .security import create_access_token, decode_access_token

# Crear tablas en base a los modelos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reviews API",
    version="1.0.0",
    description="Plataforma de reseñas con análisis de sentimiento usando Gemini.",
)

# CORS: pon aquí tu URL de GitHub Pages
FRONTEND_ORIGIN = "https://maguinda.github.io/reviews-frontend"  # <-- CAMBIA ESTO

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "https://maguinda.github.io","http://localhost:5173", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ===================== AUTH =====================

@app.post("/register")
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    crud.create_user(db, payload.email, payload.password)
    return {"message": "Usuario creado con éxito"}


@app.post("/token", response_model=schemas.TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # form.username = email
    user = crud.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}


# ===================== HELPER: obtener email desde el token =====================

def get_current_email(authorization: str = Header(None)) -> str:
    """
    Lee el header Authorization: Bearer <token>
    y devuelve el email (sub) si el token es válido.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta header Authorization",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de Authorization inválido",
        )

    token = parts[1]
    try:
        email = decode_access_token(token)  # tu función en security
        return email
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ===================== API PROTEGIDA: POST /reviews =====================

@app.post("/reviews", response_model=schemas.ReviewOut)
def crear_review(
    payload: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_email: str = Depends(get_current_email),
):
    # 1) Analizar sentimiento con Gemini
    sentimiento = gemini_client.analizar_sentimiento(payload.texto_resena)
    # Debe devolver "positivo" | "negativo" | "neutro"

    # 2) Guardar en la DB
    review = crud.create_review(
        db=db,
        producto=payload.producto,
        texto_resena=payload.texto_resena,
        sentimiento=sentimiento,
        usuario_email=current_email,
    )

    # 3) FastAPI lo serializa a ReviewOut
    return review


# ===================== API PÚBLICA: GET /reviews/{producto} =====================

@app.get("/reviews/{producto}", response_model=List[schemas.ReviewOut])
def list_reviews(producto: str, db: Session = Depends(get_db)):
    """
    Endpoint público:
    Devuelve TODAS las reseñas de un producto (con sentimiento, email, fecha, etc.)
    """
    reviews = crud.get_reviews_by_product(db, producto)
    return reviews
