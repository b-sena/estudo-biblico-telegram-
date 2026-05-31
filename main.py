import os
import time
import requests
from datetime import datetime, timedelta, timezone

# ============================================================
# CONFIGURAÇÃO
# ============================================================
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
WPPCONNECT_URL     = os.getenv("WPPCONNECT_URL")
WPPCONNECT_TOKEN   = os.getenv("WPPCONNECT_TOKEN")
WPPCONNECT_SESSION = os.getenv("WPPCONNECT_SESSION")

PHONE_1 = os.getenv("WPPCONNECT_PHONE_1")   # Seu número
PHONE_2 = os.getenv("WPPCONNECT_PHONE_2")   # Outro número

# Para ativar o grupo, remova o comentário abaixo e adicione o secret no GitHub:
# GROUP_ID = os.getenv("WPPCONNECT_GROUP")  # 120363040976590973@g.us

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não definida")

# ============================================================
# TEMAS DA SEMANA
# ============================================================
WEEK_THEMES = {
    0: {"title": "Atributos de Deus",            "focus": "santidade, soberania, bondade, fidelidade e justiça"},
    1: {"title": "Cristo e o evangelho",           "focus": "encarnação, cruz, ressurreição, graça e senhorio de Jesus"},
    2: {"title": "Oração e dependência de Deus",  "focus": "vida de oração, confiança, clamor e perseverança"},
    3: {"title": "Sofrimento, fé e perseverança", "focus": "dor, consolo, esperança e firmeza em meio às lutas"},
    4: {"title": "Vida cristã e santificação",    "focus": "obediência, arrependimento, fruto do Espírito e crescimento"},
    5: {"title": "Igreja, comunhão e serviço",    "focus": "corpo de Cristo, unidade, dons e serviço ao próximo"},
    6: {"title": "Esperança, consolo e adoração", "focus": "segurança em Deus, adoração e esperança futura"},
}

WEEKDAY_PT = {
    0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira",
    3: "quinta-feira",  4: "sexta-feira", 5: "sábado", 6: "domingo",
}

BRT      = timezone(timedelta(hours=-3))
today    = datetime.now(BRT)
date_str = today.strftime("%d/%m/%Y")
weekday  = WEEKDAY_PT[today.weekday()]
theme    = WEEK_THEMES[today.weekday()]

PROMPT = f"""
Você é um pastor e teólogo evangélico.
Hoje é {weekday}, {date_str}.
Tema da semana: {theme["title"]}
Foco do estudo: {theme["focus"]}

Gere um estudo bíblico diário formatado EXATAMENTE assim para WhatsApp:

*✍️ [Título do estudo]*

📜 *Texto:* [Livro capítulo:versículos] _(NVT)_

---

*📖 Contexto Histórico*
[2-3 linhas sobre o contexto]

*🔍 Reflexão*
[Reflexão teológica profunda mas simples, 4-6 linhas]

*🙏 Aplicação Prática*
[Como aplicar no dia a dia, 3-4 linhas]

*💭 Para Meditar*
_[Uma pergunta para reflexão pessoal]_

━━━━━━━━━━━━━━━━━
_Que a Palavra de Deus ilumine o seu dia!_ ☀️

Regras:
- Use exatamente os emojis e marcações acima
- Negrito com *asteriscos*, itálico com _underline_
- Tradução NVT
- Linguagem simples e pastoral
- Sem linguagem acadêmica
- Máximo 500 palavras no total
- Não inclua cabeçalho, apenas o conteúdo a partir do título
"""

# ============================================================
# GERAR ESTUDO COM GEMINI
# ============================================================
MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

def generate_study():
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    last_error = None
    for model in MODELS:
        wait_time = 2
        for attempt in range(1, 5):
            try:
                print(f"Tentando modelo {model} | tentativa {attempt}")
                response = client.models.generate_content(model=model, contents=PROMPT)
                study = (response.text or "").strip()
                if not study:
                    raise ValueError("Resposta vazia")
                print(f"Sucesso com modelo {model}")
                return study, model
            except Exception as e:
                last_error = e
                error_text = str(e).upper()
                if any(x in error_text for x in ["503", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                    print(f"Erro temporário ({e}). Nova tentativa em {wait_time}s")
                    time.sleep(wait_time)
                    wait_time *= 2
                    continue
                raise
    raise last_error

# ============================================================
# ENVIAR PELO WPPCONNECT
# ============================================================
def send_whatsapp(message: str, phone: str) -> None:
    url = f"{WPPCONNECT_URL}/api/{WPPCONNECT_SESSION}/send-message"
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {WPPCONNECT_TOKEN}",
    }
    payload = {
        "phone":   phone,
        "isGroup": "@g.us" in phone,
        "message": message,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Enviado para {phone}: {resp.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para {phone}: {e}")

# ============================================================
# MAIN
# ============================================================
def main():
    try:
        study, model_used = generate_study()

        header = (
            f"🏄 *Bola de Neve Camaquã*\n"
            f"📖 *Estudo Bíblico Diário*\n"
            f"_{weekday.capitalize()}, {date_str}_\n\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🏷️ *Tema:* {theme['title']}\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
        )

        msg = header + study

        send_whatsapp(msg, PHONE_1)
        send_whatsapp(msg, PHONE_2)

        # Para ativar o grupo, remova o comentário abaixo:
        # send_whatsapp(msg, GROUP_ID)

        print(f"Estudo enviado com sucesso usando {model_used}")

    except Exception as e:
        error_msg = f"❌ Falha ao gerar o estudo bíblico.\n\nData: {date_str}\n\nErro: {str(e)}"
        send_whatsapp(error_msg, PHONE_1)
        print(f"Erro: {e}")
        raise

if __name__ == "__main__":
    main()