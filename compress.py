import os
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaVideo
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Set up Telegram API credentials
API_ID = os.environ.get('API_ID', '23990433')
API_HASH = os.environ.get('API_HASH', 'e6c4b6ee1933711bc4da9d7d17e1eb20')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '5830549215:AAFPIBMULsTr6WpnIXkM1Ics7Xdv1wJn9Ys')

# Set up the Pyrogram client
app = Client('my_bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Command handler for /start
@app.on_message(filters.command('start'))
async def start_command(bot, message):
    await message.reply_text('Welcome to the video compressor bot! Send me a video file to compress.')

# Command handler for /help
@app.on_message(filters.command('help'))
async def help_command(bot, message):
    await message.reply_text('Send me a video file to compress. I will compress it and send it back to you.')

# Handler for incoming video messages
@app.on_message(filters.video)
async def compress_video(bot, message):
    # Download the video file
    original_file = await message.download()

    # Get video duration
    probe = ffmpeg.probe(original_file)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(video_info['duration'])
    
    # Compress the video file with progress bar
    progress = 0
    def progress_callback(progress_bar):
        nonlocal progress
        new_progress = int(progress_bar.progress * 100)
        if new_progress > progress:
            progress = new_progress
            await message.edit_text(f'Compressing... {progress}%')

    compressed_file = os.path.splitext(original_file)[0] + '_compressed.mp4'
    (
        ffmpeg
        .input(original_file)
        .output(compressed_file, vcodec='libx265', crf=28, preset='fast')
        .global_args('-progress', 'pipe:1')
        .overwrite_output()
        .run_async(pipe_stdout=True, pipe_stderr=True, quiet=True, progress_callback=progress_callback)
    )

    # Send the compressed video file back to the user
    await message.reply_video(video=compressed_file)

    # Clean up the downloaded files
    os.remove(original_file)
    os.remove(compressed_file)

def main():
    app.run()

if __name__ == '__main__':
    main()
