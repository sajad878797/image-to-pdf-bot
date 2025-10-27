import os
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image
from io import BytesIO

# تخزين الصور مؤقتًا
user_images = {}

# زر البداية
def get_main_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📤 ارسل صور", callback_data="start")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("اهلا بيك! ارسللي صورك حتى احولها PDF", reply_markup=get_main_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start":
        await query.edit_message_text("ارسللي الصور وحدة وحدة، ولما تخلص كلي /done")

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    user_images.setdefault(user_id, []).append(image_bytes)
    await update.message.reply_text("✅ صورة انضافت. كلي /done لما تخلص.")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    images = user_images.get(user_id, [])
    if not images:
        await update.message.reply_text("ماكو صور بعد. ارسللي صور أول.")
        return

    pdf_bytes = BytesIO()
    pil_images = [Image.open(BytesIO(img)).convert("RGB") for img in images]
    pil_images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pil_images[1:])
    pdf_bytes.seek(0)

    await update.message.reply_document(document=pdf_bytes, filename="converted.pdf")
    user_images[user_id] = []

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("كلي /start وبلّش ترسل صورك، ولما تخلص كلي /done")

def main():
    bot_token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
