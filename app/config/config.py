import os
from pathlib import Path
from dotenv import load_dotenv
from .database_manager import DatabaseConnection

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / 'configs.env'

load_dotenv(ENV_PATH)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT','51504'))
}

def get_db_connection():
    return DatabaseConnection(**DB_CONFIG)

#mudando nome para evitar conflito
get_db_manager = get_db_connection

class Config:
    #Api email Brevo
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'Sistema Hemocentro <amolvr.piton@gmail.com>')
    EMAIL_ADMIN = os.getenv('EMAIL_ADMIN', 'amolvr.piton@gmail.com')
    EMAIL_SUPORTE = os.getenv('EMAIL_SUPORTE', os.getenv('EMAIL_ADMIN', 'amolvr.piton@gmail.com'))
    
    #URL base
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
    
    #JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta-aqui')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sua-chave-jwt-aqui')
    
    #Config geral
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')