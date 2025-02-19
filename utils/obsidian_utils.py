import re

def clean_obsidian_links(text):
    """Removes Obisdian-style [[Links]] but keeps the text inside."""
    return re.sub(r"\[\[(.+?)\]\]", r"\1", text)
