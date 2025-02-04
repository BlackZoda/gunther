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

    # Check if any column contains long text
    long_text_column = any(len(row[-1]) > MAX_COLUMN_WIDTH for row in table[1:])

    # If any column has long text, switch to list-style formatting
    if long_text_column:
        embed = discord.Embed(title="Formatted Table", color=discord.Color.blue())

        for row in table[1:]:  # Skip the header
            # Dynamically unpack each row based on the number of columns
            fields = [f"**{table[0][i]}**: {row[i]}" for i in range(len(row))]
            wrapped_fields = "\n\n".join([textwrap.fill(field, width=MAX_COLUMN_WIDTH) for field in fields])
            embed.add_field(name=f"Row {table.index(row)}", value=wrapped_fields, inline=False)

        return [embed]

    # Otherwise, format as a regular table
    embed = create_single_table_embed(table)
    embeds.append(embed)

    return embeds

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

def create_single_table_embed(table):
    """Creates an individual embed for the table."""
    embed = discord.Embed(title="Formatted Table", color=discord.Color.blue())

    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]

    def format_row(row):
        return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row)))

    header_text = format_row(table[0])
    separator = "-|-".join("-" * w for w in col_widths)
    row_texts = [format_row(row) for row in table[1:]]

    table_str = f"```{header_text}\n{separator}\n" + "\n".join(row_texts) + "```"

    embed.description = table_str
    return embed

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

