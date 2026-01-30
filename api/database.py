import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega o .env (apenas para ambiente local, na Vercel ele ignora)
load_dotenv()

# Puxa os dados das variáveis de ambiente
user = os.getenv("DB_USER")
# O or "" evita que o quote_plus falhe caso a senha não seja lida
raw_password = os.getenv("DB_PASSWORD") or ""
password = quote_plus(raw_password)
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Montagem da URL com SSL obrigatório para Supabase + Vercel
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

# O pool_pre_ping=True ajuda a manter a conexão viva e reconectar se cair
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
