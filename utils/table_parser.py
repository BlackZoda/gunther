import discord

import discord

from utils.obsidian_utils import clean_obsidian_links

def create_table_embed(table):
    """Creates a properly formatted Discord embed for tables."""
    if len(table) < 2 or any(len(row) != len(table[0]) for row in table):
        embed = discord.Embed(title="Formatted Table", description="Invalid table format.", color=discord.Color.red())
        return [embed]

    # Determine column widths
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]

    def format_row(row):
        return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row)))

    # Format header and separator
    header = format_row(table[0])
    separator = " | ".join("-" * col_widths[i] for i in range(len(table[0])))
    body = "\n".join(format_row(row) for row in table[1:])

    # Properly format table as a code block
    table_str = f"```\n{header}\n{separator}\n{body}\n```"

    # Create an embed
    embed = discord.Embed(title="Formatted Table", description=table_str, color=discord.Color.blue())
    return [embed]

def create_paragraph_table(table):
    """Creates paragraph-style formatted table output."""
    headers = table[0]
    rows = table[1:]
    output = []
    for row in rows:
        entry = "\n".join(f"**{headers[i]}:** {row[i] if i < len(row) else ''}" for i in range(len(headers)))
        output.append(entry)
    return output

def parse_markdown_table(md_text):
    """Parses a Markdown table into a list of lists, preserving empty cells."""
    rows = md_text.strip().split("\n")
    if len(rows) < 3:
        return []
    
    # Prcess header
    header = [clean_obsidian_links(col.strip()) for col in rows[0].strip("|").split("|")]
    if header[0] == "":
        header[0] = " "  # Preserve leading empty cell instead of shifting
    table = [header]
    
    # PRocess table body
    for row in rows[2:]:

        row_data = [clean_obsidian_links(col.strip()) for col in row.split("|")]

        if row_data[0] == "":
            row_data[0] = " "  # Ensure first column remains correctly positioned

        row_data = row_data[1:-1]

        while len(row_data) < len(header):
            row_data.append("")  # Ensure each row has the same number of columns
        table.append(row_data[:len(header)])  # Truncate excess columns if needed

    return table
