import re

def clean_obsidian_links(text):
    """
    Removes Obsidian-style [[Links]] while preserving aliases if present.
    For example:
      [[Willpower (WP)|Willpower]]  → Willpower
      [[Round|Rounds]]             → Rounds
      [[Deafened]]                 → Deafened
    Finally, any stray '[[' or ']]' is removed.
    """
    # Replace alias links: [[Something|Alias]] → Alias
    text = re.sub(r"\[\[([^|\]]+)\|([^]]+)\]\]", r"\2", text)
    # Replace simple links: [[Link]] → Link
    text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
    # Remove any stray brackets that might be left behind
    text = text.replace('[[', '').replace(']]', '')
    return text

