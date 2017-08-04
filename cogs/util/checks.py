from discord.ext import commands


def is_dev():
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in ctx.bot.DEVELOPERS
    return commands.check(predicate)

def is_host():
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id == ctx.bot.BOT_HOSTER
    return commands.check(predicate)
