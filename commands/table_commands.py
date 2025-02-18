from discord.ext import commands

def setup_table_commands(bot, table_buffer, table_mode):
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

