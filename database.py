import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus  # ESTA LINHA É ESSENCIAL

load_dotenv()

# Substitua com os dados que você pegou no Supabase
# Formato: postgresql://[user]:[password]@[host]:[port]/[database]
# Puxa os dados do arquivo .env de forma segura
user = os.getenv("DB_USER")
password = quote_plus(os.getenv("DB_PASSWORD"))
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
