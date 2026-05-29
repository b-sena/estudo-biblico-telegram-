import os
import requests
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não definida")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID não definido")

client = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = """
Você é um pastor e teólogo evangélico.

Crie um estudo bíblico diário.

Formato:

📖 Tema

📚 Texto Bíblico

🏛 Contexto Histórico

🧠 Reflexão Teológica

🙏 Aplicação Prática

❓ Pergunta para Meditação

🤲 Oração Final

Regras:

- até 500 palavras
- linguagem simples
- profundidade teológica
- português do Brasil
- não usar linguagem acadêmica
- não repetir temas comuns
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=PROMPT
)

study = response.text

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": study
}

requests.post(
    url,
    data=payload,
    timeout=30
)

print("Estudo enviado.")