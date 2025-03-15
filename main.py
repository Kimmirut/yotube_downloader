import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from pytube import YouTube

from config import Config, load_congig

# Set up logging
logging.basicConfig(level=logging.INFO)

# Replace 'YOUR_BOT_TOKEN' with the token from BotFather
config: Config = load_congig()
BOT_TOKEN = config.tg_bot.token

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Function to download YouTube video
@dp.message(lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
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

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
