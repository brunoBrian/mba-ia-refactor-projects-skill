import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'loja.db')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
