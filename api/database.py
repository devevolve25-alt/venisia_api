import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Carrega o .env (apenas para ambiente local)
load_dotenv()

# Puxa os dados das variáveis de ambiente
user = os.getenv("DB_USER")
raw_password = os.getenv("DB_PASSWORD") or ""
password = quote_plus(raw_password)
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Montagem da URL com SSL obrigatório
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

# Engine atualizada para máxima estabilidade em ambientes Serverless (Vercel)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,       # Verifica se a conexão está viva antes de cada consulta
    pool_recycle=300,         # Recicla conexões a cada 5 minutos
    pool_size=5,              # Limita o número de conexões por instância
    max_overflow=10           # Permite uma pequena folga se houver muitos acessos
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
