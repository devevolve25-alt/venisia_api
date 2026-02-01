import os
import sys
from typing import List, Optional
from uuid import UUID
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
    
    novo_user = models.User(
        email=user.email,
        nome=user.nome,
        hashed_password=user.password, 
        plan_level=0, 
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

# --- ROTAS DE INTELIGÊNCIA E DADOS (MERCURIA, EXPLORIA, ENAS) ---

@app.post("/leads/", response_model=schemas.LeadDataSchema)
def salvar_lead(lead: schemas.LeadDataSchema, user_id: UUID, db: Session = Depends(get_db)):
    novo_lead = models.LeadData(**lead.dict(), user_id=user_id)
    try:
        db.add(novo_lead)
        db.commit()
        db.refresh(novo_lead)
        return novo_lead
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar lead: {e}")

@app.post("/diagnostics/", response_model=schemas.DiagnosticSchema)
def salvar_diagnostico(diag: schemas.DiagnosticSchema, user_id: UUID, db: Session = Depends(get_db)):
    novo_diag = models.Diagnostic(**diag.dict(), user_id=user_id)
    try:
        db.add(novo_diag)
        db.commit()
        db.refresh(novo_diag)
        return novo_diag
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar diagnóstico: {e}")

# --- ROTA DE PROCESSAMENTO IA COM TAXÍMETRO ---

@app.post("/ia/processar")
def processar_ia(
    user_id: UUID, 
    entidade: str, 
    pergunta: str, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    # Lógica de Bloqueio (ENAS Strategy)
    custo_acao = 0
    if entidade == "CriarIA":
        if user.criaria_tokens <= 0:
            raise HTTPException(status_code=402, detail="Saldo insuficiente na CriarIA.")
        custo_acao = 1
    elif entidade == "MercurIA":
        if user.status_pagamento != "pago" and user.plan_level == 0:
            # Futura lógica de limite para Leads aqui
            pass

    try:
        resposta = ai_service.perguntar_ao_panteao(pergunta, user.nome)

        # Registro de Uso
        log_uso = models.UsageRecord(
            user_id=user.id,
            entidade=entidade,
            tipo_acao="Consulta",
            categoria_uso="ADDON" if entidade == "CriarIA" else "CORE",
            creditos_debitados=custo_acao
        )
        db.add(log_uso)

        if entidade == "CriarIA":
            user.criaria_tokens -= custo_acao
        if entidade == "MercurIA":
            user.mercuria_usage_counter += 1

        db.commit()
        return {"resposta": resposta, "saldo_restante": user.criaria_tokens}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro IA: {str(e)}")

# --- FINANCEIRO E PAGAMENTOS ---

@app.patch("/users/{user_id}/payment")
def atualizar_assinatura(user_id: UUID, plano: str, tokens: int = 0, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário inexistente.")
    
    user.plan_name = plano
    user.status_pagamento = "pago"
    user.criaria_tokens += tokens 
    
    db.commit()
    return {"status": "Pagamento processado", "novo_saldo": user.criaria_tokens}
