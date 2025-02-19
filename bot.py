import os
import discord
from discord.ext import commands

from config import TOKEN, ATTACHMENT_DIR
from commands.table_commands import setup_table_commands
from events.message_handler import handle_message

os.makedirs("./tmp", exist_ok=True)
print(ATTACHMENT_DIR)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
table_buffer = {}  
table_mode = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    await handle_message(bot, message, table_buffer, table_mode)

setup_table_commands(bot, table_buffer, table_mode)

bot.run(TOKEN)

