from utils.email_fetcher import fetch_emails

def setup_email_commands(bot):
    @bot.command(name="fetchmail")
    async def fetchmail(ctx):
        """Manually fetch emails with a bot command."""
        await ctx.send("Fetching emails...")
        await fetch_emails(bot, ctx, ctx.channel)



