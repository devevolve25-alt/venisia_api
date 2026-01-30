from . import models, schemas, database
# Ou se der erro de importação relativa:
# import api.models, api.schemas, api.database
ffrom fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas

# Cria as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vendisia API")

@app.get("/")
def home():
    return {"status": "Panteão Online"}

# ROTA PARA CADASTRAR USUÁRIO
@app.post("/usuarios/", response_model=schemas.UserResponse)
def cadastrar_usuario(usuario: schemas.UserCreate, db: Session = Depends(get_db)):
    # Verifica se o e-mail já existe
    db_user = db.query(models.User).filter(models.User.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    
    # Cria o novo usuário (A senha aqui está pura, depois vamos criptografar!)
    novo_usuario = models.User(
        email=usuario.email,
        username=usuario.username,
        hashed_password=usuario.password 
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario
    
from typing import List

# ROTA PARA LISTAR TODOS OS USUÁRIOS
@app.get("/usuarios/", response_model=List[schemas.UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.User).all()
    return usuarios
    
    
import ai_service # Importa o arquivo que criamos acima

@app.get("/ia/consulta")
def consultar_oraculo(pergunta: str, db: Session = Depends(get_db)):
    # 1. Busca todos os usuários no banco
    usuarios = db.query(models.User).all()
    
    # 2. Transforma em uma lista simples de nomes para a IA não se confundir
    lista_nomes = [u.username for u in usuarios]
    
    # 3. Envia para o serviço de IA
    resposta = ai_service.perguntar_ao_panteao(pergunta, lista_nomes)
    
    return {"pergunta": pergunta, "resposta_do_oraculo": resposta}
