import os
from email.header import decode_header

from config import ALLOWED_EXTENSIONS, ATTACHMENT_DIR

def extract_text_from_email(msg):
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

