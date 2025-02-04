import os
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

def parse_markdown_table(md_text):
  rows = md_text.strip().split("\n")

  table = []
  header = rows[0].strip().split("|")
  table.append([col.strip() for col in header if col.strip()])

  for row in rows[2:]:
    row_data = row.strip().split("|")
    table.append([col.strip() for col in row_data if col.strip()])

  print("Parsed Table:", table)
  return table

def create_table_embed(table):
    """Creates properly formatted embeds for tables, handling long text more gracefully."""
    embeds = []

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

    # Otherwise, attempt to format as a regular table
    total_width = sum(col_widths) + (3 * (len(table[0]) - 1))

    if total_width > MAX_DISCORD_WIDTH:
        embeds.extend(split_wide_table(table, col_widths))  # Keep old split-table functionality
    else:
        embeds.append(create_single_table_embed(table))  # Standard table formatting for short text

    return embeds

def split_wide_table(table, col_widths):
  """Splits the table into multiple embeds if necessary."""
  embeds = []

  # If only two columns, no need to split
  if len(table[0]) < 3:
    embeds.append(create_single_table_embed(table, "Formatted Table"))
    return embeds

  # First embed: Difficulty & Modifiers
  first_table = [[row[0], row[1]] for row in table]
  embeds.append(create_single_table_embed(first_table, "Difficulty & Modifiers"))

  # Second embed: Example column as a list
  second_embed = discord.Embed(title="Examples", color=discord.Color.blue())
  examples_text = "\n".join(f"**{row[0]}**: {row[2]}" for row in table[1:])
  second_embed.description = f"```{examples_text}```"
  embeds.append(second_embed)

  return embeds

def create_single_table_embed(table, title="Formatted Table"):
  """Creates an individual embed for a table section."""
  embed = discord.Embed(title=title, color=discord.Color.blue())

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

