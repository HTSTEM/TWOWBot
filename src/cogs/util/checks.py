import inspect

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
        args = ctx.message.content.split(' ')[1:] #this is really hacky, if someone can do better please make PR
        names = inspect.getfullargspec(ctx.command.callback)[0][2:]
        kwargs = dictionary = dict(zip(names, args))
        if 'identifier' not in kwargs:
            if ctx.channel.id not in ctx.bot.servers:
                await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
                raise ctx.bot.ErrorAlreadyShown()
        else:
            identifier = kwargs['identifier']
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                raise ctx.bot.ErrorAlreadyShown()
        return True
    return commands.check(predicate)

def is_twow_owner():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.bot.server_data[ctx.channel.id]['owner'] != ctx.author.id:
            return False
        return True
    return commands.check(predicate)

def is_twow_host():
    async def predicate(ctx: commands.Context) -> bool:
        sd = ctx.bot.server_data[ctx.channel.id]
        if sd['owner'] == ctx.author.id:
            return True
        elif len(sd['queue']) > 0 and sd['queue'][0] == ctx.author.id:
            return True
        return False
    return commands.check(predicate)

def can_queue():
    async def predicate(ctx: commands.Context) -> bool:
        return ctx.bot.server_data[ctx.channel.id]['canqueue']
    return commands.check(predicate)

def can_manage():#maybe needed, keep just in case
    async def predicate(ctx: commands.Context) -> bool:
        perms = ctx.channel.permissions_for(ctx.author)
        return perms.manage_channels
    return commands.check(predicate)

def in_twow():
    async def predicate(ctx: commands.Context) -> bool:
        args = ctx.message.content.split(' ')[1:] #this is really hacky, if someone can do better please make PR
        names = inspect.getfullargspec(ctx.command.callback)[0][2:]
        kwargs = dictionary = dict(zip(names, args))
        identifier = kwargs['identifier']
        s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
        if identifier not in s_ids:
            await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
            raise ctx.bot.ErrorAlreadyShown()
        elif ctx.bot.get_channel(s_ids[identifier]).guild.get_member(ctx.author.id) != None:
            return True
        await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
        raise ctx.bot.ErrorAlreadyShown()
    return commands.check(predicate)

    
