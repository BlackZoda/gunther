from dotenv import load_dotenv
import os
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN') or ""
TABLE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)
