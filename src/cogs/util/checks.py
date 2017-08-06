from discord.ext import commands


def is_dev():
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in ctx.bot.DEVELOPERS
    return commands.check(predicate)

def is_host():
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id == ctx.bot.BOT_HOSTER
    return commands.check(predicate)

def no_sudo():
    def predicate(ctx: commands.Context) -> bool:
        return True
    return commands.check(predicate)

def twow_exists():
    async def predicate(ctx: commands.Context) -> bool:
        if 'identifier' not in ctx.kwargs:
            if ctx.channel.id not in ctx.bot.servers:
                await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
                raise ctx.bot.ErrorAlreadyShown()
        else:
            identifier = ctx.kwargs['identifier']
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                raise ctx.bot.ErrorAlreadyShown()
        return True
    return commands.check(predicate)

def is_twow_host():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.bot.server_data[ctx.channel.id]['owner'] != ctx.author.id:
            return False
        return True
    return commands.check(predicate)

    