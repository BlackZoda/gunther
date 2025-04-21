from utils.time_utils import return_time, generate_history

def setup_time_commands(bot):
    
    @bot.command(name="time")
    async def time(ctx):
        await ctx.send(return_time())
    
    @bot.command(name="history")
    async def history(ctx):
        history = await generate_history()
        await ctx.send(history)