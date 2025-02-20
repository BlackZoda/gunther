import os
import discord
from config import DISCORD_FILE_LIMIT

async def post_to_discord(channel, subject, sender, date, body, attachment_paths):
    """Posts processed emails to Discord"""
    await channel.send(f"**New Email from {sender}:**\n\nSubject: {subject}\nDate: {date}\n\n{body}")

    for file_path in attachment_paths:
        file_size = os.path.getsize(file_path)

        if file_size > DISCORD_FILE_LIMIT:
            await channel.send(f"⚠️ Attachment too large to upload: `{os.path.basename(file_path)}` ({file_size / (1024*1024):.2f} MB)")
        else:
            with open(file_path, "rb") as file:
                await channel.send(file=discord.File(file, filename=os.path.basename(file_path)))

        os.remove(file_path)
