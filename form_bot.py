import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8277969955:AAEzitYId_cH5rKXXTdotpfw1LOX2Us6nCk"
CHANNEL_ID = -1002722852436

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {"key": "name", "text": "1. Как тебя зовут?"},
    {"key": "age", "text": "2. Сколько тебе лет?"},
    {"key": "location", "text": "3. Где ты находишься?"},
    {"key": "instagram", "text": "4. Ссылочка на Instagram"},
    {
        "key": "has_of",
        "text": "5. Уже есть аккаунт OnlyFans?",
        "options": ["Да", "Нет", "Пока нет, но готова начать"],
    },
    {
        "key": "show_face",
        "text": "6. Готова ли показывать лицо в контенте?",
        "options": ["Да", "Нет", "Зависит от контента"],
    },
    {
        "key": "contact_method",
        "text": "7. Удобный способ связи",
        "options": ["Email", "Telegram", "Instagram", "WhatsApp"],
    },
    {"key": "contact_info", "text": "8. Контактная информация"},
    {"key": "extra", "text": "9. Что еще хочешь рассказать о себе (Опционально)"},
]

user_states = {}

def get_next_question(state):
    step = state["step"]
    if step < len(QUESTIONS):
        q = QUESTIONS[step]
        if "options" in q:
            return q["text"], q["options"]
        else:
            return q["text"], None
    return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_states[user_id] = {"step": 0, "answers": {}}
    text, options = get_next_question(user_states[user_id])
    if options:
        markup = ReplyKeyboardMarkup([[o] for o in options], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(text, reply_markup=markup)
    else:
        await update.message.reply_text(text)


async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    message = update.message.text.strip()

    if user_id not in user_states:
        await update.message.reply_text("Пожалуйста, введите /start, чтобы начать.")
        return

    state = user_states[user_id]
    step = state["step"]

    if step >= len(QUESTIONS):
        await update.message.reply_text("Вы уже заполнили анкету. Спасибо!")
        return

    key = QUESTIONS[step]["key"]
    state["answers"][key] = message
    state["step"] += 1

    # Ask next question or finish
    if state["step"] < len(QUESTIONS):
        text, options = get_next_question(state)
        if options:
            markup = ReplyKeyboardMarkup([[o] for o in options], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(text, reply_markup=markup)
        else:
            await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("✅ Спасибо! Анкету получили, скоро свяжемся с тобой")
        await send_summary_to_channel(context, state["answers"])
        del user_states[user_id]


async def send_summary_to_channel(context, answers):
    msg = "📥 *Новая анкета:*\n\n"
    label_map = {
        "name": "Имя",
        "age": "Возраст",
        "location": "Локация",
        "instagram": "Instagram",
        "has_of": "Аккаунт OnlyFans",
        "show_face": "Показывать лицо",
        "contact_method": "Связь",
        "contact_info": "Контакт",
        "extra": "Дополнительно",
    }
    for key in QUESTIONS:
        k = key["key"]
        v = answers.get(k, "—")
        label = label_map.get(k, k.capitalize())
        msg += f"*{label}:* {v}\n"

    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    print("Бот запущен...")
    app.run_polling()