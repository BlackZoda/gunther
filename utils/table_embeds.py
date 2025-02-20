import discord

from config import MAX_LINE_LENGTH

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
