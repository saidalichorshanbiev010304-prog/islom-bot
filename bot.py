import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

PROMPT = """Sen islom dini boyicha bilimli yordamchisan.
Quron oyatlari, hadislar, suralar haqida soralsa:
Arab matni, Transliteratsiya, Uzbek tarjimasi, Qisqacha tafsir, Manba formatida javob ber.
Har doim uzbek tilida yoz."""

def groq_javob(savol):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": savol}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Xatolik: " + str(e)

def bosh_menyu():
    keyboard = [
        [InlineKeyboardButton("Oyat izlash", callback_data="oyat"),
         InlineKeyboardButton("Hadis izlash", callback_data="hadis")],
        [InlineKeyboardButton("Sura malumoti", callback_data="sura"),
         InlineKeyboardButton("Duolar", callback_data="dua")],
        [InlineKeyboardButton("Islom asoslari", callback_data="asoslar"),
         InlineKeyboardButton("Kunlik oyat", callback_data="kunlik")],
        [InlineKeyboardButton("Muhammadsodiq Audio", callback_data="audio"),
         InlineKeyboardButton("Tasodifiy hadis", callback_data="tasodifiy")],
    ]
    return InlineKeyboardMarkup(keyboard)

def orqaga():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Bosh menyu", callback_data="bosh")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum!\n\nIslom Bilim Markazi Botiga xush kelibsiz!\n\nMenyudan tanlang:",
        reply_markup=bosh_menyu()
    )

async def tugma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "bosh":
        await query.message.edit_text("Menyudan tanlang:", reply_markup=bosh_menyu())
    elif data == "oyat":
        context.user_data["rejim"] = "oyat"
        await query.message.edit_text("Qaysi oyatni izlaysiz?\nMisol: Fotiha 1 yoki Baqara 255", reply_markup=orqaga())
    elif data == "hadis":
        context.user_data["rejim"] = "hadis"
        await query.message.edit_text("Qaysi mavzuda hadis?\nMisol: sabr, ilm, namoz", reply_markup=orqaga())
    elif data == "sura":
        context.user_data["rejim"] = "sura"
        await query.message.edit_text("Qaysi sura haqida?\nMisol: Fotiha, Yasin, Mulk", reply_markup=orqaga())
    elif data == "dua":
        context.user_data["rejim"] = "dua"
        await query.message.edit_text("Qaysi mavzuda dua?\nMisol: safar, shifo, imtihon", reply_markup=orqaga())
    elif data == "asoslar":
        await query.message.edit_text("Yuklanmoqda...")
        javob = groq_javob("Islomning 5 rukni va imonning 6 sharti haqida toliq malumot ber")
        await query.message.edit_text(javob, reply_markup=orqaga())
    elif data == "kunlik":
        await query.message.edit_text("Yuklanmoqda...")
        javob = groq_javob("Bugungi kun uchun ilhomlantiruvchi Quron oyatini toliq manosi bilan ber")
        await query.message.edit_text(javob, reply_markup=orqaga())
    elif data == "tasodifiy":
        await query.message.edit_text("Yuklanmoqda...")
        javob = groq_javob("Tasodifiy sahih hadis ber arab matni tarjima va manba bilan")
        await query.message.edit_text(javob, reply_markup=orqaga())
    elif data == "audio":
        await query.message.edit_text("Muhammadsodiq Muhammad Yusuf\nAudio Kutubxona:\n\nhttps://muhammadsodiq.uz\n\nYouTube:\nhttps://youtube.com/@muhammadsodiqmuhammadyusuf", reply_markup=orqaga())

async def xabar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = update.message.text
    rejim = context.user_data.get("rejim", "umumiy")
    msg = await update.message.reply_text("Javob tayyorlanmoqda...")
    if rejim == "oyat":
        javob = groq_javob("Quron " + matn + " oyatini arab matni transliteratsiya va uzbek tarjimasi bilan ber")
    elif rejim == "hadis":
        javob = groq_javob(matn + " haqida sahih hadis ber manba va tarjima bilan")
    elif rejim == "sura":
        javob = groq_javob(matn + " surasi haqida toliq malumot ber")
    elif rejim == "dua":
        javob = groq_javob(matn + " uchun dua ber arab transliteratsiya va tarjima bilan")
    else:
        javob = groq_javob(matn)
    context.user_data["rejim"] = "umumiy"
    await msg.edit_text(javob, reply_markup=orqaga())

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(tugma))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xabar))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()