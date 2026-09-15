import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get('SUPABASE_URL')
key: str = os.environ.get('SUPABASE_KEY')

if url and key and 'cole_sua_url_aqui' not in url:
    supabase: Client = create_client(url, key)
else:
    supabase = None
    print('AVISO: Configure o arquivo .env com as chaves do Supabase.')
