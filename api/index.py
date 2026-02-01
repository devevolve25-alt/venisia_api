import os
import sys
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

# 1. AJUSTE DE CAMINHO
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. IMPORTAÇÕES
import models
import schemas
from database import engine, get_db
import ai_service

# 3. INICIALIZAÇÃO DO BANCO
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Aviso ao criar tabelas: {e}")

# 4. CONFIGURAÇÃO DA API
app = FastAPI(title="Vendisia API - O Panteão")

@app.get("/")
def home():
    return {
        "status": "Panteão Online",
        "ambiente": "Vercel + Supabase",
        "docs": "/docs"
    }

# --- GESTÃO DE USUÁRIOS E PLANOS ---

@app.post("/users/", response_model=schemas.UserResponse)
def cadastrar_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado!")
    
    # Criando com os novos campos de negócio do ENAS
    novo_user = models.User(
        email=user.email,
        nome=user.nome,
        hashed_password=user.password, # Lembre-se de usar hash real no futuro
        plan_level=0, # Começa como Lead
        plan_name="Lead",
        status_pagamento="pendente"
    )
    
    try:
        db.add(novo_user)
        db.commit()
        db.refresh(novo_user)
        return novo_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {str(e)}")

@app.get("/users/", response_model=List[schemas.UserResponse])
def listar_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# --- ROTA DE INTELIGÊNCIA COM TRAVA DE CRÉDITOS ---

@app.post("/ia/processar")
def processar_ia(
    user_id: str, 
    entidade: str, # 'MercurIA', 'ExplorIA', 'CriarIA'
    pergunta: str, 
    db: Session = Depends(get_db)
):
    # 1. Buscar usuário e verificar permissões
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # 2. Lógica de Bloqueio Baseada no Relatório do ENAS
    if entidade == "CriarIA":
        if user.criaria_tokens <= 0:
            raise HTTPException(status_code=402, detail="Saldo de créditos da CriarIA insuficiente.")
        custo_acao = 1 # Definido pelo ENAS
    else:
        # MercurIA e ExplorIA rodam sob Assinatura
        if user.status_pagamento != "pago" and user.plan_level == 0:
            # Leads podem usar a ExplorIA 1 vez (exemplo de regra)
            pass 
        custo_acao = 0

    try:
        # 3. Chamar a IA
        resposta = ai_service.perguntar_ao_panteao(pergunta, user.nome)

        # 4. Registrar o Uso (O Taxímetro)
        log_uso = models.UsageRecord(
            user_id=user.id,
            entidade=entidade,
            tipo_acao="Consulta",
            categoria_uso="ADDON" if entidade == "CriarIA" else "CORE",
            creditos_debitados=custo_acao
        )
        db.add(log_uso)

        # 5. Debitar saldo se for CriarIA
        if entidade == "CriarIA":
            user.criaria_tokens -= custo_acao
        
        # 6. Incrementar uso justo da MercurIA
        if entidade == "MercurIA":
            user.mercuria_usage_counter += 1

        db.commit()
        return {"resposta": resposta, "saldo_restante": user.criaria_tokens}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

# --- ROTA PARA ATUALIZAR PAGAMENTOS (Pelo n8n ou Checkout) ---

@app.patch("/users/{user_id}/payment")
def atualizar_assinatura(user_id: str, plano: str, tokens: int = 0, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário inexistente.")
    
    user.plan_name = plano
    user.status_pagamento = "pago"
    user.criaria_tokens += tokens # Adiciona créditos se for compra de Add-on
    
    db.commit()
    return {"status": "Perfil atualizado com sucesso", "novo_saldo": user.criaria_tokens}
