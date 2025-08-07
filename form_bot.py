import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          ConversationHandler, ContextTypes, filters)

# States
(NAME, AGE, LOCATION, INSTAGRAM, OF_ACCOUNT, FACE_OK, CONTACT_METHOD, CONTACT_INFO, EXTRA) = range(9)

# Keyboard options
of_account_keyboard = [['Да', 'Нет', 'Пока нет, но готова начать']]
face_keyboard = [['Да', 'Нет', 'Зависит от контента']]
contact_keyboard = [['Email', 'Telegram', 'Instagram', 'WhatsApp']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1. Как тебя зовут?")
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("2. Сколько тебе лет?")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    await update.message.reply_text("3. Где ты находишься?")
    return LOCATION

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['location'] = update.message.text
    await update.message.reply_text("4. Ссылочка на Instagram")
    return INSTAGRAM

async def instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['instagram'] = update.message.text
    await update.message.reply_text(
        "5. Уже есть аккаунт OnlyFans?",
        reply_markup=ReplyKeyboardMarkup(of_account_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return OF_ACCOUNT

async def of_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['of_account'] = update.message.text
    await update.message.reply_text(
        "6. Готова ли показывать лицо в контенте?",
        reply_markup=ReplyKeyboardMarkup(face_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return FACE_OK

async def face_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['face_ok'] = update.message.text
    await update.message.reply_text(
        "7. Удобный способ связи",
        reply_markup=ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CONTACT_METHOD

async def contact_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact_method'] = update.message.text
    await update.message.reply_text("8. Контактная информация", reply_markup=ReplyKeyboardRemove())
    return CONTACT_INFO

async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact_info'] = update.message.text
    await update.message.reply_text("9. Что еще хочешь рассказать о себе (Опционально)")
    return EXTRA

async def extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['extra'] = update.message.text

    data = context.user_data
    summary = (
        f"📥 Новая анкета:\n"
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Локация: {data['location']}\n"
        f"Instagram: {data['instagram']}\n"
        f"OnlyFans: {data['of_account']}\n"
        f"Показывает лицо: {data['face_ok']}\n"
        f"Связь: {data['contact_method']} — {data['contact_info']}\n"
        f"Дополнительно: {data['extra']}"
    )

    CHANNEL_ID = "-1002722852436"
    await context.bot.send_message(chat_id=os.getenv("ADMIN_CHAT_ID"), text=summary)

    await update.message.reply_text("✅ Спасибо! Анкету получили, скоро свяжемся с тобой")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    import asyncio

    BOT_TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
            INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, instagram)],
            OF_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, of_account)],
            FACE_OK: [MessageHandler(filters.TEXT & ~filters.COMMAND, face_ok)],
            CONTACT_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_method)],
            CONTACT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_info)],
            EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, extra)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Бот запущен...")
    app.run_polling()
