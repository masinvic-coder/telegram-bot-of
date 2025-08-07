import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8277969955:AAHjwdGW0WX6CGd0c2jhTkNvilkmKcy6N98"
CHANNEL_ID = -1002722852436

logging.basicConfig(level=logging.INFO)

QUESTIONS = [
    {"key": "name", "text": "1. What’s your name?"},
    {"key": "age", "text": "2. How old are you?"},
    {"key": "location", "text": "3. Where are you based?"},
    {"key": "instagram", "text": "4. Instagram link"},
    {
        "key": "has_of",
        "text": "5. Do you already have an OnlyFans account?",
        "options": ["Yes", "No", "Not yet, but I’m ready to start"],
    },
    {
        "key": "show_face",
        "text": "6. Are you okay with showing your face in content?",
        "options": ["Yes", "No", "Depends on the content"],
    },
    {
        "key": "contact_method",
        "text": "7. How would you prefer we contact you?",
        "options": ["Email", "Telegram", "Instagram DM", "WhatsApp"],
    },
    {"key": "contact_info", "text": "8. Contact information"},
    {"key": "extra", "text": "9. Anything else you want to tell us?"},
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
        await update.message.reply_text("Please type /start to begin.")
        return

    state = user_states[user_id]
    step = state["step"]

    if step >= len(QUESTIONS):
        await update.message.reply_text("You’ve already completed the form. Thank you!")
        return

    key = QUESTIONS[step]["key"]
    state["answers"][key] = message
    state["step"] += 1

    if state["step"] < len(QUESTIONS):
        text, options = get_next_question(state)
        if options:
            markup = ReplyKeyboardMarkup([[o] for o in options], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(text, reply_markup=markup)
        else:
            await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("✅ Thank you! Your application has been submitted.")
        await send_summary_to_channel(context, state["answers"])
        del user_states[user_id]


async def send_summary_to_channel(context, answers):
    msg = "📥 *New Application Submitted:*\n\n"
    label_map = {
        "name": "Name",
        "age": "Age",
        "location": "Location",
        "instagram": "Instagram",
        "has_of": "OnlyFans Account",
        "show_face": "Show Face",
        "contact_method": "Preferred Contact Method",
        "contact_info": "Contact Info",
        "extra": "Extra Notes",
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

    print("Bot is running...")
    app.run_polling()