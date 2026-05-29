import os
import time
import smtplib
import requests
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não definida")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID não definido")

client = genai.Client(api_key=GEMINI_API_KEY)

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

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

BRT = timezone(timedelta(hours=-3))
today = datetime.now(BRT)

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

def generate_study():
    last_error = None

    for model in MODELS:
        wait_time = 2

        for attempt in range(1, 5):
            try:
                print(f"Tentando modelo {model} | tentativa {attempt}")

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                study = (response.text or "").strip()

                if not study:
                    raise ValueError("Resposta vazia")

                print(f"Sucesso com modelo {model}")
                return study, model

            except Exception as e:
                last_error = e
                error_text = str(e).upper()

                retryable = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                )

                if retryable:
                    print(f"Erro temporário ({e}). Nova tentativa em {wait_time}s")
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue

                raise

    raise last_error

def send_telegram(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Telegram aceita até 4096 caracteres por mensagem após o parsing.
    # Vamos enviar em blocos menores para evitar erro.
    max_chunk_size = 3900

    chunks = []
    text = message.strip()

    while text:
        if len(text) <= max_chunk_size:
            chunks.append(text)
            break

        split_at = text.rfind("\n", 0, max_chunk_size)
        if split_at == -1:
            split_at = max_chunk_size

        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()

    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "disable_web_page_preview": True,
        }

        response = requests.post(telegram_url, data=payload, timeout=30)
        response.raise_for_status()

def send_email(subject, body):
    if not EMAIL_USER or not EMAIL_APP_PASSWORD or not EMAIL_TO:
        print("Configuração de e-mail ausente. Pulando envio por e-mail.")
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_APP_PASSWORD)
        server.send_message(msg)

try:
    study, model_used = generate_study()

    telegram_message = f"""
Estudo Bíblico Diário

Data: {date_str}
Dia: {weekday_pt}
Tema: {theme["title"]}
Modelo: {model_used}

{study}
"""

    email_subject = f"Estudo Bíblico Diário - {date_str}"
    email_body = f"""Estudo Bíblico Diário

Data: {date_str}
Dia: {weekday_pt}
Tema: {theme["title"]}
Modelo: {model_used}

{study}
"""

    send_telegram(telegram_message)
    send_email(email_subject, email_body)

    print(f"Estudo enviado com sucesso usando {model_used}")

except Exception as e:
    error_message = f"""
❌ Falha ao gerar o estudo bíblico.

Data: {date_str}

Erro:
{str(e)}
"""

    try:
        send_telegram(error_message)
    except Exception:
        pass

    print(f"Erro ao gerar ou enviar estudo: {e}")
    raise