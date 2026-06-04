# FitBot 🏋️

Bot de Telegram com inteligência artificial para dúvidas de treino e nutrição.

## O que ele faz

- Responde dúvidas sobre treino e nutrição usando IA
- Menu interativo com botões
- Guias de treino para hipertrofia, força e emagrecimento
- Guias de dieta para ganho de massa, perda de gordura e manutenção
- Histórico de conversa separado por usuário
- Comando /reset para limpar o histórico

## Tecnologias usadas

- Python
- python-telegram-bot
- Groq API (LLaMA 3.3)
- requests

## Como rodar

1. Instale as dependências:
pip install python-telegram-bot requests

2. Adicione seus tokens no código:
TELEGRAM_TOKEN = "seu_token_aqui"
GROQ_API_KEY = "sua_chave_aqui"

3. Rode o bot:
python bot.py

## Comandos

- /start — Menu principal
- /reset — Limpar histórico da conversa
- /ajuda — Mostrar comandos disponíveis