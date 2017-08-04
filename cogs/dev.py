import inspect

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import checks
#all of these need to be dev only

class Core():

    @commands.command(aliases=['quit', 'kill'])
    @checks.is_dev()
    async def die(self, ctx):
        '''Disconnects the bot.'''
        await ctx.bot.send_message(ctx.channel, ':wave:')
        await ctx.bot.logout()

    @commands.command()
    @checks.is_dev()
    async def say(self, ctx, channel:int, *, words:str):  # Say somethin'
        channel = ctx.bot.get_channel(channel)
        if channel is not None:
            await ctx.bot.send_message(channel, words)

    @commands.command()
    @checks.is_dev()
    async def role_ids(self, ctx):  # DM a list of the IDs of all the roles
        await ctx.bot.send_message(ctx.author,
            '\n'.join(['{}: {}'.format(role.name.replace('@', '@\u200b'), role.id) for role in ctx.guild.roles]))
        await ctx.bot.send_message(ctx.channel,':mailbox_with_mail:')

    @commands.command(aliases=['eval'])
    @checks.is_host()
    async def evaluate(self, ctx, *, code:str):
        result = None
        env = {
            'channel': ctx.channel,
            'author': ctx.author,
            'self': ctx.bot,
            'message': ctx.message,
            'channel': ctx.channel,
            'save_data': ctx.bot.save_data,
            'ctx': ctx,
            'bot': ctx.bot,
        }
        env.update(globals())

        try:
            result = eval(code, env)

            if inspect.isawaitable(result):
                result = await result

            colour = 0x00FF00
        except Exception as e:
            result = type(e).__name__ + ': ' + str(e)
            colour = 0xFF0000

        embed = discord.Embed(colour=colour, title=code, description='```py\n{}```'.format(result))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        try:
            await ctx.channel.send(embed=embed)
        except discord.errors.Forbidden:
            pass

def setup(bot):
    bot.add_cog(Core())
