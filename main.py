import asyncio
import os

from pytube import YouTube
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update, Message, FSInputFile

from config import Config, load_congig

async def handle_webhook(request):
    """Handle incoming updates from Telegram."""
    update = await request.json()
    telegram_update = Update.model_validate(update)  # Correct validation in Aiogram v3
    bot = request.app["bot"]  # ✅ Now bot is stored in app
    dp = request.app["dp"]  # ✅ Dispatcher is stored too

    await dp.feed_update(bot, telegram_update)  # Correct method for handling updates
    return web.Response()


async def main() -> None:
    # Loading config
    config: Config = load_congig()

    # Initializing bot and dispatcher
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.message.register(youtube_download, is_yt_link)

    # Webhook settings
    WEBHOOK_HOST = config.tg_bot.webhook_url  # Example: "https://your-bot.onrender.com"
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
    WEBAPP_HOST = "0.0.0.0"
    WEBAPP_PORT = int(config.tg_bot.port)  # Use PORT from config/env

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)

    # Create web server
    app = web.Application()
    app["bot"] = bot  # ✅ Store bot in the app context
    app["dp"] = dp  # ✅ Store dispatcher in the app context
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBAPP_PORT)
    await site.start()

    while True:
        await asyncio.sleep(3600)  # Keep running


async def youtube_download(message: Message):
    try:
        await message.reply("📥 Downloading the video, please wait...")

        # Download the video
        video_path = download_video(message.text)

        video = FSInputFile(video_path)

        # Send the video file as a document (no compression)
        await message.reply_document(video)

        # Delete the file after sending
        os.remove(video_path)
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

def download_video(url):
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    file_path = video.download()
    return file_path


def is_yt_link(message: str) -> bool:
    return "youtube.com" in message.text or "youtu.be" in message.text
