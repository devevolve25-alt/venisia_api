from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- USUÁRIO ---

# O que chega no cadastro
class UserCreate(BaseModel):
    email: EmailStr
    nome: str
    password: str

# O que a API devolve (Segurança: nunca devolvemos o password)
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    nome: Optional[str]
    plan_level: int
    plan_name: str
    status_pagamento: str
    criaria_tokens: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- LEADS E DIAGNÓSTICOS ---

class LeadDataSchema(BaseModel):
    empresa_nome: Optional[str]
    setor_atuacao: Optional[str]
    dor_principal: Optional[str]
    temperatura_lead: str = "frio"
    score_conversao: int = 0

    class Config:
        from_attributes = True

class DiagnosticSchema(BaseModel):
    url_analisada: Optional[str]
    pontuacao_geral: Optional[int]
    estimativa_perda_financeira: Optional[Decimal]
    enviado_por_email: bool = False

    class Config:
        from_attributes = True

# --- USO E FINANCEIRO ---

class UsageRecordSchema(BaseModel):
    entidade: str
    tipo_acao: str
    categoria_uso: str # CORE ou ADDON
    tokens_estimados: int = 0
    creditos_debitados: int = 0

    class Config:
        from_attributes = True

class TransactionSchema(BaseModel):
    item_comprado: str
    valor_bruto: Decimal
    status_transacao: str
    metodo_pagamento: Optional[str]

    class Config:
        from_attributes = True
