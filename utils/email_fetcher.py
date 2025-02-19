import os
import imaplib, email
from email.header import decode_header

from discord import Attachment

from config import (IMAP_SERVER, IMAP_PORT, EMAIL_USER, EMAIL_PASSWORD,
    GUILD_ID, DEFAULT_CHANNEL_ID)

async def fetch_emails(bot, ctx, channel=None):
    """Fetch unread emails, process text and attachments, and send them to Discord."""
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
    print("Extracting attachments...")
    pass

async def post_to_discord(channel, subject, sender, date, body, attachment_paths):
    await channel.send(f"**New Email from {sender}:**\n\nSubject: {subject}\nDate: {date}\n\n{body}")
    print(attachment_paths)
