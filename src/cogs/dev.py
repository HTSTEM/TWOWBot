import subprocess
import inspect
import sys

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import checks
#all of these need to be dev only


class Dev():
    @commands.command(aliases=['quit', 'kill'])
    @checks.is_dev()
    async def die(self, ctx):
        '''Disconnects the bot.'''
        await ctx.bot.send_message(ctx.channel, ':wave:')
        await ctx.bot.logout()

    @commands.command()
    @checks.is_dev()
    async def say(self, ctx, channel:int, *, words:str):
        '''Get te bot to say something.
        *Why did I even think this was a good idea?*
        '''
        channel = ctx.bot.get_channel(channel)
        if channel is not None:
            await ctx.bot.send_message(channel, words)

    @commands.command()
    @checks.is_dev()
    async def role_ids(self, ctx):
        '''Get all of the role ids for the server.
        '''
        await ctx.bot.send_message(ctx.author,
            '\n'.join(['{}: {}'.format(role.name.replace('@', '@\u200b'), role.id) for role in ctx.guild.roles]))
        await ctx.bot.send_message(ctx.channel,':mailbox_with_mail:')

    @commands.command()
    @checks.is_dev()
    async def sudo(self, ctx, *, cmd:str):
        '''Run a command ignoring every check.
        This will work for all commands unless they have the
        `checks.no_sudo` check applied, in which case, sudo will
        refuse to run the command.
        '''

        ctx.message.content = ctx.prefix + cmd
        await ctx.bot.process_commands_sudo(ctx.message)

    @commands.command(aliases=['gitpull'])
    @checks.is_dev()
    async def git_pull(self, ctx):
        '''Pull from git and update the bot.'''
        async with ctx.channel.typing():
            if sys.platform == 'win32':
                process = subprocess.run('git pull', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.stdout, process.stderr
            else:
                process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()

            stdout = stdout.decode()
            stderr = stderr.decode()

        await ctx.bot.send_message(ctx.channel, '```diff\n{}\n{}```'.format(stdout.replace('```', '`\u200b`\u200b`'), stderr.replace('```', '`\u200b`\u200b`')))

    @commands.command()
    @checks.is_host()
    @checks.no_sudo()
    async def git_cli(self, ctx):
        '''Start a CLI for `git`.'''
    
        await ctx.bot.send_message(ctx.channel, '`git` CLI started! `:q` to quit.')

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and (m.content.startswith('git ') or m.content == ':q')

        resp = None
        async with ctx.channel.typing():
            while resp != ':q':
                resp = (await ctx.bot.wait_for('message', check=check)).content
                if resp == ':q':
                    break
                
                if sys.platform == 'win32':
                    process = subprocess.run('git ' + resp[4:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.stdout, process.stderr
                else:
                    process = await asyncio.create_subprocess_exec('git', resp[4:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = await process.communicate()

                stdout = stdout.decode()
                stderr = stderr.decode()

                await ctx.bot.send_message(ctx.channel, '```diff\n{}\n{}```'.format(stdout.replace('```', '`\u200b`\u200b`'), stderr.replace('```', '`\u200b`\u200b`')))
        await ctx.bot.send_message(ctx.channel, 'You have left the `git` CLI.')

    @commands.command(aliases=['eval'])
    @checks.is_host()
    @checks.no_sudo()
    async def evaluate(self, ctx, *, code:str):
        '''Run some code.
        The environment currently includes:
         `channel`
         `author`
         `bot`
         `message`
         `channel`
         `save_data`
         `ctx`
        '''
        result = None
        env = {
            'channel': ctx.channel,
            'author': ctx.author,
            'bot': ctx.bot,
            'message': ctx.message,
            'channel': ctx.channel,
            'save_data': ctx.bot.save_data,
            'ctx': ctx,
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
    bot.add_cog(Dev())
