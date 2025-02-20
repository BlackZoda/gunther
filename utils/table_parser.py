import discord

import discord

from utils.obsidian_utils import clean_obsidian_links

def create_table_embed(table):
    """Creates a properly formatted Discord embed for tables, splitting if necessary."""
    if len(table) < 2 or any(len(row) != len(table[0]) for row in table):
        embed = discord.Embed(title="Formatted Table", 
                              description="Invalid table format.", 
                              color=discord.Color.red())
        return [embed]
    
    # Determine maximum width for each column (based on all rows)
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]
    
    def format_row(row):
        # Format each cell left-justified with no extra pipes at start/end.
        return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row))).rstrip()
    
    # Format the header row.
    header = format_row(table[0])
    
    # Build the separator.
    sep_parts = []
    for i in range(len(table[0])):
        if i == len(table[0]) - 1:
            # For the last column, use one dash longer than the header text.
            desired = len(table[0][i]) + 1
            sep_parts.append("-" * desired)
        else:
            sep_parts.append("-" * col_widths[i])
    separator = " | ".join(sep_parts)
    
    # Optional: if the separator line is too long, collapse it into a fixed string.
    MAX_LINE_LENGTH = 100
    if len(separator) > MAX_LINE_LENGTH:
        separator = "-" * MAX_LINE_LENGTH
    
    # Format body rows.
    body = "\n".join(format_row(row) for row in table[1:])
    
    # Construct the table string inside a code block.
    table_str = f"```\n{header}\n{separator}\n{body}\n```"
    
    # Split into multiple embeds if necessary (Discord embed description limit is 4096 chars)
    max_embed_length = 4096
    embeds = []
    if len(table_str) <= max_embed_length:
        embed = discord.Embed(title="Formatted Table", description=table_str, color=discord.Color.blue())
        embeds.append(embed)
    else:
        lines = table_str.split("\n")
        current_desc = ""
        for line in lines:
            if len(current_desc) + len(line) + 1 > max_embed_length:
                embed = discord.Embed(title="Formatted Table", description=current_desc, color=discord.Color.blue())
                embeds.append(embed)
                current_desc = line + "\n"
            else:
                current_desc += line + "\n"
        if current_desc:
            embed = discord.Embed(title="Formatted Table", description=current_desc, color=discord.Color.blue())
            embeds.append(embed)
    
    return embeds

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
