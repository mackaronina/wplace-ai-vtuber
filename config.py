import os

from dotenv import load_dotenv

load_dotenv()

AUDIO_CHUNK_SIZE = 1024
TOTAL_ITERATIONS = 5
RESOURCE_URL = 'http://127.0.0.1:8000/static'
TEMPERATURE = 1.2
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_MODEL_NAME = '@cf/meta/llama-4-scout-17b-16e-instruct'
