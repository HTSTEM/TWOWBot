import subprocess
import asyncio
import inspect
import sys

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import checks


class Core:
    '''Core commands'''
    @commands.command(aliases=['quit', 'kill'])
    @checks.is_developer()
    async def die(self, ctx):
        '''Disconnects the bot from Discord.'''
        await ctx.send('Logging out...')
        await ctx.bot.logout()

    @commands.command()
    @checks.is_developer()
    async def crash(self, ctx):
        '''Crash the bot'''
        raise Exception("Yeah baby. Errors for all!")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        '''Loads an extension'''
        try:
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Loaded cog {} successfully!'.format(cog))

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        '''Unloads an extension'''
        try:
            ctx.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send('\N{OK HAND SIGN} Unloaded cog {} successfully!'.format(cog))

    @commands.group(invoke_without_command=True)
    @checks.is_developer()
    async def reload(self, ctx, *, cog: str):
        '''Reloads an extension'''
        try:
            ctx.bot.unload_extension(cog)
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load: `{}`\n```py\n{}\n```'.format(cog, e))
        else:
            await ctx.send('\N{OK HAND SIGN} Reloaded cog {} successfully'.format(cog))

    @reload.command(name='all')
    @checks.is_developer()
    async def reload_all(self, ctx):
        '''Reloads all extensions'''
        for extension in ctx.bot.extensions.copy():
            ctx.bot.unload_extension(extension)
            try:
                ctx.bot.load_extension(extension)
            except Exception as e:
                await ctx.send('Failed to load `{}`:\n```py\n{}\n```'.format(extension, e))
                return

        await ctx.send('\N{OK HAND SIGN} Reloaded {} cogs successfully'.format(len(ctx.bot.extensions)))

    @commands.command(aliases=['git_pull'])
    @checks.is_staff()
    async def update(self, ctx):
        '''Updates the bot from git'''

        await ctx.send(':warning: Warning! Pulling from git!')

        if sys.platform == 'win32':
            process = subprocess.run('git pull', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.stdout, process.stderr
        else:
            process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await process.communicate()
        stdout = stdout.decode().splitlines()
        stdout = '\n'.join('+ ' + i for i in stdout)
        stderr = stderr.decode().splitlines()
        stderr = '\n'.join('- ' + i for i in stderr)

        await ctx.send('`Git` response: ```diff\n{}\n{}```'.format(stdout, stderr))

    @commands.command(aliases=['eval'])
    @commands.is_owner()
    async def debug(self, ctx, *, code: str):
        '''Evaluates code'''

        result = None

        env = {
            'ctx': ctx,
            'bot': ctx.bot,
            'guild': ctx.guild,
            'author': ctx.author,
            'message': ctx.message,
            'channel': ctx.channel
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
        await ctx.send(embed=embed)

    @commands.command()
    @checks.is_developer()
    async def reloadconfig(self, ctx):
        with open('config.yml', 'r') as f:
            ctx.bot.config = yaml.load(f, Loader=yaml.Loader)
        await ctx.send('Reloaded config file.')


def setup(bot):
    bot.add_cog(Core())
