from dotenv import load_dotenv
import os
import re

load_dotenv()

# Discord Settings
TOKEN = os.getenv('DISCORD_BOT_TOKEN') or ""
GUILD_ID = os.getenv('DISCORD_GUILD_ID') or ""
DEFAULT_CHANNEL_ID = os.getenv('DISCORD_DEFAULT_CHANNEL_ID') or ""

# Email Settings
EMAIL_USER = os.getenv('EMAIL_USER') or ""
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') or ""
IMAP_SERVER = os.getenv('IMAP_SERVER') or ""
IMAP_PORT = os.getenv('IMAP_PORT') or 993
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".mp3", ".mp4", ".wav", ".webm", ".doc", ".docx"}
ATTACHMENT_DIR = "./tmp/"

# Table Settings
TABLE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)

