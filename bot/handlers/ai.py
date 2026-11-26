import asyncio
from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import APIError

from bot.services.todo_service import (
    get_todos_tool,
    add_todo_tool,
    update_todo_tool,
)

from bot.services.poma_service import (
    add_poma_tool,
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
user_chats = {}

# Основная модель и резервные на случай 503 перегрузки
MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]

def register_ai_handlers(bot):

    @bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
    async def ai_assistant(message, telegram_profile):
        try:
            await bot.send_chat_action(message.chat.id, 'typing')
        except Exception:
            pass

        user = telegram_profile.user

        config = types.GenerateContentConfig(
            system_instruction=(
                f"Ты персональный ассистент в Telegram. "
                f"ID текущего пользователя в базе данных: {user.id} (имя: {user.username}). "
                f"Всегда передавай user_id={user.id} при вызове ЛЮБЫХ функций (инструментов). "
                "Если пользователь просит показать дела, добавить задачи (даже списком), "
                "отметить выполненной или удалить — вызывай функции работы с задачами. "
                "Если пользователь сообщает, сколько часов или помидорок (poma) он поработал над проектом — "
                "вызывай add_poma_tool. "
                "Отвечай дружелюбно, лаконично и по делу, используй эмодзи."
            ),
            tools=[get_todos_tool, add_todo_tool, update_todo_tool, add_poma_tool],
            temperature=0.2,
        )

        for model_name in MODELS:
            # Если чата еще нет или предыдущая модель упала с 503 — создаем новый
            if user.id not in user_chats or user_chats[user.id]["model"] != model_name:
                user_chats[user.id] = {
                    "model": model_name,
                    "chat": client.aio.chats.create(model=model_name, config=config),
                }

            chat = user_chats[user.id]["chat"]

            for attempt in range(2):
                try:
                    response = await chat.send_message(message.text)
                    await bot.reply_to(message, response.text)
                    return

                except APIError as e:
                    print(f"DEBUG [{model_name}] APIError: code={e.code}, message={e.message}")
                    if e.code == 503:
                        if attempt == 0:
                            await asyncio.sleep(1.5)
                            continue
                        # Удаляем сломанный чат и пробуем следующую модель из списка MODELS
                        user_chats.pop(user.id, None)
                        break

                    user_chats.pop(user.id, None)
                    await bot.reply_to(message, "⚠️ Произошла техническая ошибка при обращении к ИИ.")
                    return

                except Exception as e:
                    print(f"DEBUG Unexpected error: {e}")
                    user_chats.pop(user.id, None)
                    await bot.reply_to(message, f"⚠️ Произошла ошибка: {e}")
                    return

        await bot.reply_to(message, "⏳ Все серверы ИИ сейчас временно перегружены, попробуй через пару минут.")
