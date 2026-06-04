import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

# ── Configurações ──────────────────────────
TELEGRAM_TOKEN = "seu_token_aqui"
GROQ_API_KEY   = "sua_chave_groq_aqui"

# ── Histórico por usuário ──────────────────
# Dicionário que guarda um histórico separado para cada usuário
historicos = {}

def get_historico(user_id):
    if user_id not in historicos:
        historicos[user_id] = []
    return historicos[user_id]

# ── Personalidade do bot ───────────────────
SYSTEM_PROMPT = """Você é um personal trainer virtual chamado FitBot.
Responda dúvidas sobre treino, nutrição e saúde de forma direta e motivadora.
Seja objetivo, use linguagem simples e informal.
Nunca invente informações médicas sérias — indique um profissional quando necessário."""

# ── Chama a IA (Groq) ──────────────────────
def chamar_groq(mensagens):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": mensagens
    }
    resposta = requests.post(url, headers=headers, json=body)
    return resposta.json()["choices"][0]["message"]["content"]

# ── Comando /start ─────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botoes = [
        [InlineKeyboardButton("💪 Treino", callback_data="menu_treino")],
        [InlineKeyboardButton("🥗 Dieta", callback_data="menu_dieta")],
        [InlineKeyboardButton("ℹ️ O que este bot pode fazer", callback_data="info")],
    ]
    await update.message.reply_text(
        "Olá! Eu sou o *FitBot*, seu personal trainer virtual! 🏋️\n\nO que você precisa hoje?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botoes)
    )

# ── Comando /reset ─────────────────────────
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    historicos[user_id] = []
    await update.message.reply_text("🔄 Histórico limpo! Podemos começar do zero.")

# ── Comando /ajuda ─────────────────────────
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Comandos disponíveis:*\n\n"
        "/start — Menu principal\n"
        "/reset — Limpar histórico da conversa\n"
        "/ajuda — Mostrar esta mensagem\n\n"
        "Ou é só mandar uma mensagem direta que eu respondo!",
        parse_mode="Markdown"
    )

# ── Resposta dos botões ────────────────────
async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    historico = get_historico(user_id)

    if data == "menu_treino":
        botoes = [
            [InlineKeyboardButton("🏋️ Hipertrofia", callback_data="treino_hipertrofia")],
            [InlineKeyboardButton("⚡ Força", callback_data="treino_forca")],
            [InlineKeyboardButton("🏃 Emagrecimento", callback_data="treino_emagrecimento")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar")],
        ]
        await query.message.reply_text(
            "💪 *Qual seu objetivo de treino?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(botoes)
        )

    elif data == "menu_dieta":
        botoes = [
            [InlineKeyboardButton("📈 Ganho de massa", callback_data="dieta_massa")],
            [InlineKeyboardButton("📉 Perda de gordura", callback_data="dieta_gordura")],
            [InlineKeyboardButton("⚖️ Manutenção", callback_data="dieta_manutencao")],
            [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar")],
        ]
        await query.message.reply_text(
            "🥗 *Qual seu objetivo de dieta?*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(botoes)
        )

    elif data == "voltar":
        botoes = [
            [InlineKeyboardButton("💪 Treino", callback_data="menu_treino")],
            [InlineKeyboardButton("🥗 Dieta", callback_data="menu_dieta")],
            [InlineKeyboardButton("ℹ️ O que este bot pode fazer", callback_data="info")],
        ]
        await query.message.reply_text(
            "O que você precisa hoje?",
            reply_markup=InlineKeyboardMarkup(botoes)
        )

    elif data == "info":
        await query.message.reply_text(
            "🤖 *O que eu posso fazer:*\n\n"
            "💪 Montar treinos personalizados\n"
            "🥗 Dar dicas de dieta e nutrição\n"
            "❓ Responder dúvidas sobre saúde e exercícios\n"
            "💬 Lembrar o contexto da nossa conversa\n\n"
            "É só me mandar uma mensagem!",
            parse_mode="Markdown"
        )

    else:
        perguntas = {
            "treino_hipertrofia":   "Me dê um guia resumido de treino para hipertrofia muscular.",
            "treino_forca":         "Me dê um guia resumido de treino para ganho de força.",
            "treino_emagrecimento": "Me dê um guia resumido de treino para emagrecimento.",
            "dieta_massa":          "Me dê um guia resumido de dieta para ganho de massa muscular.",
            "dieta_gordura":        "Me dê um guia resumido de dieta para perda de gordura.",
            "dieta_manutencao":     "Me dê um guia resumido de dieta para manutenção do peso.",
        }
        pergunta = perguntas.get(data)
        if pergunta:
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            historico.append({"role": "user", "content": pergunta})
            texto = chamar_groq([{"role": "system", "content": SYSTEM_PROMPT}] + historico)
            historico.append({"role": "assistant", "content": texto})
            limite = 4000
            for i in range(0, len(texto), limite):
                await query.message.reply_text(texto[i:i+limite])

# ── Mensagens normais ──────────────────────
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    historico = get_historico(user_id)
    mensagem = update.message.text
    await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
    historico.append({"role": "user", "content": mensagem})
    try:
        texto = chamar_groq([{"role": "system", "content": SYSTEM_PROMPT}] + historico)
        historico.append({"role": "assistant", "content": texto})
        limite = 4000
        for i in range(0, len(texto), limite):
            await update.message.reply_text(texto[i:i+limite])
    except Exception as e:
        print("ERRO:", e)
        await update.message.reply_text("Erro interno, tenta de novo.")

# ── Iniciar bot ────────────────────────────
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("ajuda", ajuda))
app.add_handler(CallbackQueryHandler(botao))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
print("Bot rodando...")
app.run_polling()