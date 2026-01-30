import os
import sys
# Garante que o Python encontre os arquivos na pasta api
sys.path.append(os.path.join(os.path.dirname(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importação direta (sem o ponto se o sys.path.append estiver lá)
import models, schemas, database, ai_service
from database import engine, get_db

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importações internas ajustadas para o ambiente Vercel
from . import models, schemas, database, ai_service
from .database import engine, get_db

# Cria as tabelas ao iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vendisia API")

@app.get("/")
def home():
    return {"status": "Panteão Online"}

# ROTA PARA CADASTRAR USUÁRIO
@app.post("/usuarios/", response_model=schemas.UserResponse)
def cadastrar_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    
    novo_usuario = models.User(
        email=usuario.email,
        username=usuario.username,
        hashed_password=usuario.password 
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

# ROTA PARA LISTAR TODOS OS USUÁRIOS
@app.get("/usuarios/", response_model=List[schemas.UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# ROTA DA IA
@app.get("/ia/consulta")
def consultar_oraculo(pergunta: str, db: Session = Depends(get_db)):
    usuarios = db.query(models.User).all()
    lista_nomes = [u.username for u in usuarios]
    resposta = ai_service.perguntar_ao_panteao(pergunta, lista_nomes)
    return {"pergunta": pergunta, "resposta_do_oraculo": resposta}
