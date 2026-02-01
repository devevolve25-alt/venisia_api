from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, Integer, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nome = Column(String, nullable=True) # Alinhado com o SQL recente
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    
    # CONTROLE DE ACESSO E PLANOS
    plan_level = Column(Integer, default=0)
    plan_name = Column(String, default="Lead")
    
    # FINANCEIRO
    status_pagamento = Column(String, default="pendente")
    data_vencimento = Column(TIMESTAMP(timezone=True))
    valor_assinatura_atual = Column(Numeric(10, 2), default=0.00)
    stripe_customer_id = Column(String)
    
    # USO E CRÉDITOS
    criaria_tokens = Column(Integer, default=0)
    mercuria_usage_counter = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    last_login = Column(TIMESTAMP(timezone=True))

class LeadData(Base):
    __tablename__ = "leads_data"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    empresa_nome = Column(String)
    setor_atuacao = Column(String)
    dor_principal = Column(String)
    objetivo_curto_prazo = Column(String)
    tamanho_equipe = Column(String)
    temperatura_lead = Column(String, default="frio")
    score_conversao = Column(Integer, default=0)
    estrategia_recomendada = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Diagnostic(Base):
    __tablename__ = "diagnostics"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    url_analisada = Column(String)
    pontuacao_geral = Column(Integer)
    falhas_identificadas = Column(String)
    oportunidades_ganho = Column(String)
    estimativa_perda_financeira = Column(Numeric(12, 2))
    relatorio_completo_url = Column(String)
    enviado_por_email = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class Report(Base):
    __tablename__ = "reports"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    entidade_geradora = Column(String) # ENAS, IAO, Humano
    tipo_relatorio = Column(String)
    titulo = Column(String)
    objetivos_chave = Column(String)
    passo_a_passo_acao = Column(String)
    exibir_para_cliente = Column(Boolean, default=False)
    status_implementacao = Column(String, default="planejado")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    entidade = Column(String, nullable=False)
    tipo_acao = Column(String, nullable=False)
    categoria_uso = Column(String, nullable=False) 
    tokens_estimados = Column(Integer, default=0)
    creditos_debitados = Column(Integer, default=0)
    details = Column(JSONB) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    item_comprado = Column(String, nullable=False)
    categoria_item = Column(String, nullable=False)
    valor_bruto = Column(Numeric(10, 2), nullable=False)
    status_transacao = Column(String, default="concluida")
    gateway_id = Column(String)
    metodo_pagamento = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
