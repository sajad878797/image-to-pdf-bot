import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from PIL import Image
from io import BytesIO

user_data = {}

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 ارسل صورة", callback_data="send")],
        [InlineKeyboardButton("📚 عرض الصور", callback_data="list")],
        [InlineKeyboardButton("✏️ تغيير اسم الملف", callback_data="rename")],
        [InlineKeyboardButton("✅ تحويل إلى PDF", callback_data="done")],
        [InlineKeyboardButton("🗑 حذف الكل", callback_data="confirm_clear")],
        [InlineKeyboardButton("🔄 بدء من جديد", callback_data="reset")],
        [InlineKeyboardButton("📤 مشاركة البوت", url="https://t.me/PDF97IQBOT")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"images": [], "filename": f"pdf_from_{update.effective_user.first_name}.pdf"}

    hour = datetime.now().hour
    if hour < 12:
        greeting = "🌞 صباح الخير"
    elif hour < 17:
        greeting = "🌤 هلا بالظهر"
    elif hour < 21:
        greeting = "🌇 مساء النور"
    else:
        greeting = "🌙 تصبح على خير"

    welcome_text = (
        f"{greeting} {update.effective_user.first_name}!\n\n"
        "📸 حول صورك إلى PDF بكل سهولة!\n"
        "✨ تقدر ترتب الصور، تغيّر اسم الملف، وتحصل على ملف جاهز.\n\n"
        "اضغط على الأزرار لتبدأ 👇"
    )

    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    user_data.setdefault(user_id, {"images": [], "filename": "converted.pdf"})["images"].append(image_bytes)
    await update.message.reply_text(
        "✅ صورة انضافت!\n📚 تقدر ترتب الصور، تغيّر الاسم، أو تحوّلها إلى PDF باستخدام الأزرار 👇",
        reply_markup=get_main_keyboard()
    )

async def list_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    images = user_data.get(user_id, {}).get("images", [])
    if not images:
        await update.callback_query.edit_message_text("ماكو صور بعد.", reply_markup=get_main_keyboard())
        return

    buttons = []
    for i in range(len(images)):
        buttons.append([
            InlineKeyboardButton(f"⬆️ {i+1}", callback_data=f"up_{i}"),
            InlineKeyboardButton(f"⬇️ {i+1}", callback_data=f"down_{i}")
        ])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="menu")])
    await update.callback_query.edit_message_text("رتّب الصور باستخدام الأزرار:", reply_markup=InlineKeyboardMarkup(buttons))

async def reorder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    data = query.data

    images = user_data.get(user_id, {}).get("images", [])
    if not images:
        await query.edit_message_text("ماكو صور بعد.", reply_markup=get_main_keyboard())
        return

    if data.startswith("up_"):
        idx = int(data.split("_")[1])
        if idx > 0:
            images[idx], images[idx - 1] = images[idx - 1], images[idx]
    elif data.startswith("down_"):
        idx = int(data.split("_")[1])
        if idx < len(images) - 1:
            images[idx], images[idx + 1] = images[idx + 1], images[idx]

    await list_images(update, context)

async def rename_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✏️ اكتب الاسم الجديد للملف (بدون .pdf):")
    context.user_data["awaiting_filename"] = True

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("awaiting_filename"):
        new_name = update.message.text.strip()
        if new_name:
            user_data[user_id]["filename"] = f"{new_name}.pdf"
            await update.message.reply_text(
                f"✅ تم تغيير الاسم إلى: {new_name}.pdf\n📸 تقدر تضيف صور أو ترتبها قبل التحويل 👇",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text("❌ الاسم فارغ. حاول مرة ثانية.", reply_markup=get_main_keyboard())
        context.user_data["awaiting_filename"] = False

async def confirm_clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("✅ نعم، احذف", callback_data="clear")],
        [InlineKeyboardButton("❌ لا، رجوع", callback_data="menu")]
    ]
    await update.callback_query.edit_message_text("هل أنت متأكد من حذف كل الصور؟", reply_markup=InlineKeyboardMarkup(buttons))

async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["images"] = []
    await update.callback_query.edit_message_text(
        "🗑 تم حذف كل الصور.\n📤 ارسل صور جديدة أو غيّر اسم الملف قبل التحويل 👇",
        reply_markup=get_main_keyboard()
    )

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"images": [], "filename": f"pdf_from_{update.effective_user.first_name}.pdf"}
    await update.callback_query.edit_message_text(
        "🔄 تم البدء من جديد!\n📤 ارسل أول صورة، وبعدها تقدر ترتب وتحوّل 👇",
        reply_markup=get_main_keyboard()
    )

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    images = user_data.get(user_id, {}).get("images", [])
    filename = user_data.get(user_id, {}).get("filename", "converted.pdf")

    if not images:
        await update.callback_query.edit_message_text("ماكو صور بعد.", reply_markup=get_main_keyboard())
        return

    pdf_bytes = BytesIO()
    pil_images = [Image.open(BytesIO(img)).convert("RGB") for img in images]
    pil_images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=pil_images[1:])
    pdf_bytes.seek(0)

    await update.callback_query.message.reply_document(document=InputFile(pdf_bytes, filename=filename))

    summary = (
        f"📦 تم تحويل {len(images)} صورة إلى ملف PDF\n"
        f"📁 اسم الملف: {filename}\n\n"
        "📤 تحب تشارك البوت ويا أصدقائك؟ جرب الزر أدناه 👇"
    )

    share_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 مشاركة البوت", url="https://t.me/PDF97IQBOT")],
        [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="menu")]
    ])

    await update.callback_query.message.reply_text(summary, reply_markup=share_button)
    user_data[user_id]["images"] = []

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "send":
        await query.edit_message_text("📤 ارسل صورة وحدة وحدة، ولما تخلص استخدم الأزرار 👇", reply_markup=get_main_keyboard())
    elif data == "list":
        await list_images(update, context)
    elif data == "rename":
        await rename_handler(update, context)
    elif data == "done":
        await done(update, context)
    elif data == "confirm_clear":
        await confirm_clear_handler(update, context)
    elif data == "clear":
        await clear_handler(update, context)
    elif data == "reset":
        await reset_handler(update, context)
    elif data == "menu":
        await query.edit_message_text("رجعنا للقائمة 👇", reply_markup=get_main_keyboard())
    elif data.startswith("up_") or data.startswith("down_"):
        await reorder_handler(update, context)

def main():
    bot_token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler
