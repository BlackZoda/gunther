import os
import discord
import imaplib, email
from email.header import decode_header

from discord import Attachment

from config import (IMAP_SERVER, IMAP_PORT, EMAIL_USER, EMAIL_PASSWORD,
    GUILD_ID, DEFAULT_CHANNEL_ID, ALLOWED_EXTENSIONS, ATTACHMENT_DIR, DISCORD_FILE_LIMIT)

async def fetch_emails(bot, ctx, channel=None):
    """Fetch unread emails, process text and attachments, and send them to Discord."""

    os.makedirs(ATTACHMENT_DIR, exist_ok=True)

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("INBOX")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            print("No new emails.")
            await ctx.send("No new emails.")
            return

        if channel is None:
            guild = bot.get_guild(GUILD_ID)
            channel = guild.get_channel(DEFAULT_CHANNEL_ID)

        for num in messages[0].split():
            _, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    msg = email.message_from_bytes(raw_email)

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")

                    sender = msg.get("From")
                    date = msg.get("Date")
                    body = extract_text_from_email(msg)
                    attachment_paths = extract_attachments_from_email(msg)

                    await post_to_discord(channel, subject, sender, date, body, attachment_paths)

                    mail.store(num, "+FLAGS", "\\Seen") # Mark as read

        mail.logout()

    except Exception as e:
        print(f"Error fetching emails: {e}")

def extract_text_from_email(msg):
    """Extracts and saves attachements from emails."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break
    else:
        body += msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return body.strip()

def extract_attachments_from_email(msg):
    """Extracts and saves attachements from emails."""
    attachment_paths = []
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename, encoding = decode_header(part.get_filename())[0]
            if isinstance(filename, bytes):
                filename = filename.decode(encoding or "utf-8")

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in ALLOWED_EXTENSIONS:
                file_path = os.path.join(ATTACHMENT_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(part.get_payload(decode=True))

                attachment_paths.append(file_path)
    return attachment_paths

async def post_to_discord(channel, subject, sender, date, body, attachment_paths):
    await channel.send(f"**New Email from {sender}:**\n\nSubject: {subject}\nDate: {date}\n\n{body}")

    for file_path in attachment_paths:
        file_size = os.path.getsize(file_path)

        if file_size > DISCORD_FILE_LIMIT:
            await channel.send(f"⚠️ Attachment too large to upload: `{os.path.basename(file_path)}` ({file_size / (1024*1024):.2f} MB)")
        else:
            with open(file_path, "rb") as file:
                await channel.send(file=discord.File(file, filename=os.path.basename(file_path)))

        os.remove(file_path)
