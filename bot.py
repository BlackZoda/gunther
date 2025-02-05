import os
import discord
import re
import textwrap
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN') or ""
MAX_DISCORD_WIDTH = 80
MAX_COLUMN_WIDTH = 50

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

TABLE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)

table_buffer = {}

def create_table_embed(table):
    """Creates properly formatted embeds for tables."""
    embeds = []

    # Check for invalid table structure if any row has a different number of columns
    if len(table) < 2 or any(len(row) != len(table[0]) for row in table):
        embed = discord.Embed(title="Formatted Table", description="Invalid table format.", color=discord.Color.red())
        return [embed]

    # Calculate column widths for all columns dynamically
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]

    # Helper function to create a single embed for a subset of rows
    def create_single_embed(fields):
        """Helper function to create a single embed for a subset of rows."""
        embed = discord.Embed(title="Formatted Table", color=discord.Color.blue())
        table_str = "```"

        # Add each row with proper alignment
        for field in fields:
            table_str += f"{field}\n"
        table_str += "```"

        embed.description = table_str
        return embed

    # Function to format rows with padding for missing columns
    def format_row(row, col_widths):
        """Helper function to format rows with dynamic column widths."""
        return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" if row[i] else " " * col_widths[i] for i in range(len(row)))

    # Split rows into chunks, considering both 25 fields and 6000 character limit
    max_fields_per_embed = 25
    max_characters_per_embed = 6000
    max_description_length = 4096
    fields = []

    # Add header row first
    header_row = " | ".join(table[0])
    fields.append(header_row)

    # Prepare content for embeds
    all_rows = [header_row] + [format_row(row, col_widths) for row in table[1:]]
    
    # Create a new embed when the description length exceeds the limit
    def split_into_embeds(rows):
        nonlocal embeds
        current_embed_fields = []
        current_embed_description = ""

        for row in rows:
            # Check if adding this row exceeds the embed description limit
            if len(current_embed_description) + len(row) + 3 > max_description_length:
                # Create a new embed and reset the description
                embeds.append(create_single_embed(current_embed_fields))
                current_embed_fields = [header_row]  # Start with header for new embed
                current_embed_description = ""

            # Add the row to the current embed
            current_embed_fields.append(row)
            current_embed_description += row + "\n"

        # Add the last embed if there are fields
        if current_embed_fields:
            embeds.append(create_single_embed(current_embed_fields))

    # Split into embeds
    split_into_embeds(all_rows)

    # Return the generated embeds
    return embeds

def format_row(row, col_widths):
    """Helper function to format rows with dynamic column widths."""
    return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row)))

def parse_markdown_table(md_text):
    rows = md_text.strip().split("\n")
    table = []

    # Parse the header row and remove any empty spaces at the start and end of each column
    header = rows[0].strip().split("|")
    header = [col.strip() for col in header[1:] if col.strip()]  # Skip the first empty column
    table.append(header)

    # Parse the rest of the rows, skipping the separator row and empty columns
    for row in rows[2:]:  # Skipping the second row which is the separator
        row_data = row.strip().split("|")
        row_data = [col.strip() for col in row_data]  # Remove any unwanted spaces

        # If there's an extra empty first column (before the first column of data), remove it
        if row_data[0] == '':
            row_data = row_data[1:]

        # Initialize a list to hold the correctly aligned row
        full_row_data = [''] * len(header)  # Start with empty cells equal to the header's length

        # Ensure row_data doesn't exceed header length, and insert data accordingly
        for i, col in enumerate(row_data):
            if i < len(header):  # Only insert data into columns that exist in the header
                full_row_data[i] = col
        
        # Avoid adding empty rows
        if any(cell != '' for cell in full_row_data):
            table.append(full_row_data)

    print("Parsed Table:", table)  # For debugging
    return table

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    if message.author.id in table_buffer:
        if content.lower() == "!table_end":
            full_table = "\n".join(table_buffer.pop(message.author.id))
            parsed_table = parse_markdown_table(full_table)
            embeds = create_table_embed(parsed_table)
            for embed in embeds:
                await message.channel.send(embed=embed)
        else:
            table_buffer[message.author.id].append(content)
        return

    if TABLE_PATTERN.search(content):
        parsed_table = parse_markdown_table(content)
        embeds = create_table_embed(parsed_table)
        for embed in embeds:
            await message.channel.send(embed=embed)

    await bot.process_commands(message)

@bot.command()
async def table_start(ctx):
    table_buffer[ctx.author.id] = []
    await ctx.send("Table started. Type '!table_end' to end the table.")

bot.run(TOKEN)

