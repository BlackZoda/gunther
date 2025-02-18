from utils.table_parser import parse_markdown_table, create_table_embed, create_paragraph_table
from config import TABLE_PATTERN

async def handle_message(bot, message, table_buffer, table_mode):
    if message.author.bot:
        return

    content = message.content.strip()

    if content.startswith("```") and content.endswith("```"):
        return
    
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
