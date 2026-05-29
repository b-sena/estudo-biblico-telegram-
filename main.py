import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

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

WEEK_THEMES = {
    0: {
        "title": "Atributos de Deus",
        "focus": "santidade, soberania, bondade, fidelidade e justiça",
    },
    1: {
        "title": "Cristo e o evangelho",
        "focus": "encarnação, cruz, ressurreição, graça e senhorio de Jesus",
    },
    2: {
        "title": "Oração e dependência de Deus",
        "focus": "vida de oração, confiança, clamor e perseverança",
    },
    3: {
        "title": "Sofrimento, fé e perseverança",
        "focus": "dor, consolo, esperança e firmeza em meio às lutas",
    },
    4: {
        "title": "Vida cristã e santificação",
        "focus": "obediência, arrependimento, fruto do Espírito e crescimento",
    },
    5: {
        "title": "Igreja, comunhão e serviço",
        "focus": "corpo de Cristo, unidade, dons e serviço ao próximo",
    },
    6: {
        "title": "Esperança, consolo e adoração",
        "focus": "segurança em Deus, adoração e esperança futura",
    },
}

today = datetime.now(ZoneInfo("America/Sao_Paulo"))
weekday_pt = {
    0: "segunda-feira",
    1: "terça-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sábado",
    6: "domingo",
}[today.weekday()]

theme = WEEK_THEMES[today.weekday()]
date_str = today.strftime("%d/%m/%Y")

prompt = f"""
Você é um pastor e teólogo evangélico.

Hoje é {weekday_pt}, {date_str}.

Tema da semana:
{theme["title"]}

Foco do estudo:
{theme["focus"]}

Crie um estudo bíblico diário com:

1. Título
2. Texto bíblico principal
3. Contexto histórico breve
4. Reflexão teológica profunda, mas simples
5. Aplicação prática
6. Pergunta para meditação
7. Oração final

Regras:
- até 500 palavras
- português do Brasil
- tradução da Bíblia NVT
- linguagem simples
- tom pastoral
- sem linguagem acadêmica
- sem repetir temas comuns
- escolha um texto bíblico coerente com o tema de hoje
- seja claro, bíblico e edificante
"""

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    study = (response.text or "").strip()

    if not study:
        raise ValueError("Gemini retornou texto vazio")

    message = f"""📖 *Estudo bíblico diário*

📅 Data: {date_str}
🗓 Dia: {weekday_pt}
🎯 Tema da semana: {theme["title"]}

{study}
"""

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    telegram_response = requests.post(telegram_url, data=payload, timeout=30)
    telegram_response.raise_for_status()

    print("Estudo enviado com sucesso.")

except Exception as e:
    print(f"Erro ao gerar ou enviar estudo: {e}")
    raise