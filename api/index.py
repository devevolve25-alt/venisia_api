import os
import sys
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# 1. AJUSTE DE CAMINHO (O "Pulo do Gato" para a Vercel)
# Isso permite que os arquivos dentro da pasta 'api' se enxerguem
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. IMPORTAÇÕES DOS MÓDULOS LOCAIS (Sem pontos, graças ao sys.path)
import models
import schemas
import database
import ai_service
from database import engine, get_db

# 3. INICIALIZAÇÃO DO BANCO
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Erro ao conectar no banco/criar tabelas: {e}")

# 4. CONFIGURAÇÃO DA API
app = FastAPI(title="Vendisia API")

@app.get("/")
def home():
    return {
        "status": "Panteão Online",
        "database": "Conectado",
        "docs": "/docs"
    }

# --- ROTAS DE USUÁRIO ---

@app.post("/usuarios/", response_model=schemas.UserResponse)
def cadastrar_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verifica se o e-mail já existe
    db_user = db.query(models.User).filter(models.User.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    
    # Cria o novo usuário
    novo_usuario = models.User(
        email=usuario.email,
        username=usuario.username,
        hashed_password=usuario.password 
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@app.get("/usuarios/", response_model=List[schemas.UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# --- ROTA DA IA (ORÁCULO) ---

@app.get("/ia/consulta")
def consultar_oraculo(pergunta: str, db: Session = Depends(get_db)):
    try:
        # Busca usuários para dar contexto à IA
        usuarios = db.query(models.User).all()
        lista_nomes = [u.username for u in usuarios]
        
        # Envia para o serviço de IA
        resposta = ai_service.perguntar_ao_panteao(pergunta, lista_nomes)
        return {"pergunta": pergunta, "resposta_do_oraculo": resposta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no Oráculo: {str(e)}")
