import os
import discord
import re
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN') or ""

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
TABLE_PATTERN = re.compile(r"^\s*\|.*\|\s*$", re.MULTILINE)

table_buffer = {}
table_mode = {}  # Tracks whether it's regular table or paragraph mode

def create_table_embed(table):
    """Creates properly formatted embeds for tables."""
    if len(table) < 2 or any(len(row) != len(table[0]) for row in table):
        embed = discord.Embed(title="Formatted Table", description="Invalid table format.", color=discord.Color.red())
        return [embed]
    
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]
    
    def format_row(row):
        return " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(row)))
    
    embed = discord.Embed(title="Formatted Table", color=discord.Color.blue())
    table_str = "```\n" + "\n".join(format_row(row) for row in table) + "\n```"
    embed.description = table_str
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
    
    header = [col.strip() for col in rows[0].split("|")]
    if header[0] == "":
        header[0] = " "  # Preserve leading empty cell instead of shifting
    table = [header]
    
    for row in rows[2:]:
        row_data = [col.strip() for col in row.split("|")]
        if row_data[0] == "":
            row_data[0] = " "  # Ensure first column remains correctly positioned
        while len(row_data) < len(header):
            row_data.append("")  # Ensure each row has the same number of columns
        table.append(row_data[:len(header)])  # Truncate excess columns if needed
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
            mode = table_mode.pop(message.author.id, "table")
            parsed_table = parse_markdown_table(full_table)
            if parsed_table:
                if mode == "table_p":
                    paragraphs = create_paragraph_table(parsed_table)
                    for p in paragraphs:
                        await message.channel.send(p)
                else:
                    embeds = create_table_embed(parsed_table)
                    for embed in embeds:
                        await message.channel.send(embed=embed)
            else:
                await message.channel.send("Invalid table input.")
        elif content.lower() == "!table_cancel":
            table_buffer.pop(message.author.id, None)
            table_mode.pop(message.author.id, None)
            await message.channel.send("Table input canceled.")
        else:
            table_buffer[message.author.id].append(content)
        return
    
    if TABLE_PATTERN.search(content):
        parsed_table = parse_markdown_table(content)
        if parsed_table:
            embeds = create_table_embed(parsed_table)
            for embed in embeds:
                await message.channel.send(embed=embed)
        else:
            await message.channel.send("Invalid Markdown table.")
    
    await bot.process_commands(message)

@bot.command()
async def table(ctx):
    table_buffer[ctx.author.id] = []
    table_mode[ctx.author.id] = "table"
    await ctx.send("Table input started. Use '!table_end' to finish or '!table_cancel' to abort.")

@bot.command()
async def table_p(ctx):
    table_buffer[ctx.author.id] = []
    table_mode[ctx.author.id] = "table_p"
    await ctx.send("Paragraph table input started. Use '!table_end' to finish or '!table_cancel' to abort.")

@bot.command()
async def table_cancel(ctx):
    if ctx.author.id in table_buffer:
        table_buffer.pop(ctx.author.id, None)
        table_mode.pop(ctx.author.id, None)
        await ctx.send("Table input canceled.")
    else:
        await ctx.send("No table input in progress.")

bot.run(TOKEN)

