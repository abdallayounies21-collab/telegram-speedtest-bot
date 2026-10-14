import os
import logging
import asyncio
import speedtest

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("BOT_TOKEN")


def main_menu():
    keyboard = [
        [InlineKeyboardButton("⚡ بدء فحص السرعة", callback_data="speedtest")],
        [InlineKeyboardButton("ℹ️ حول البوت", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🚀 أهلاً بيك في بوت قياس سرعة الإنترنت\n\n"
        "📡 افحص سرعة اتصالك الحقيقية\n"
        "📥 Download | 📤 Upload\n"
        "⚡ Ping | 🌐 Server\n\n"
        "اضغط الزر أدناه لبدء الفحص."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            "⚡ بوت قياس سرعة الإنترنت\n"
            "يقيس سرعة الاتصال باستخدام خادم اختبار متاح."
        )
        return

    if query.data == "speedtest":
        await query.edit_message_text(
            "⏳ جاري فحص سرعة الإنترنت...\n"
            "قد يستغرق الاختبار بعض الوقت."
        )

        try:
            result = await asyncio.to_thread(run_speedtest)

            await query.message.reply_text(
                "📊 نتائج فحص سرعة الإنترنت\n\n"
                f"📥 Download: {result['download']:.2f} Mbps\n"
                f"📤 Upload: {result['upload']:.2f} Mbps\n"
                f"📡 Ping: {result['ping']:.2f} ms\n"
                f"🌐 Server: {result['server']}\n\n"
                "✅ اكتمل الفحص"
            )

        except Exception:
            logging.exception("Speed test failed")
            await query.message.reply_text(
                "❌ تعذّر إكمال الفحص.\n"
                "حاول مرة ثانية بعد قليل."
            )


def run_speedtest():
    tester = speedtest.Speedtest()
    tester.get_best_server()

    download = tester.download() / 1_000_000
    upload = tester.upload() / 1_000_000
    ping = tester.results.ping
    server = tester.results.server.get("name", "Unknown")

    return {
        "download": download,
        "upload": upload,
        "ping": ping,
        "server": server,
    }


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    logging.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
