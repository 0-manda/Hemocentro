import os
from dotenv import load_dotenv
from .database_manager import DatabaseConnection

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'Hemocentro'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def get_db_manager():
    """Retorna uma instância de DatabaseConnection configurada."""
    return DatabaseConnection(**DB_CONFIG)