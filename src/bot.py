import traceback
import datetime
import logging
import sys
import re
import os
import base64

from discord.ext import commands
from discord.ext.commands.errors import CommandError, CommandNotFound
import ruamel.yaml as yaml
import discord


class HelperBodge():
    def __init__(self, data):
        self.data = data
    def format(self, arg):
        return self.data.format(arg.replace('@', '@\u200b'))


class TWOWBot(commands.Bot):
    class ErrorAlreadyShown(Exception): pass

    def __init__(self, log_file=None, *args, **kwargs):
        self.debug = False
        self.config = {}
        self.server_data = {}
        self.yaml = yaml.YAML(typ='safe')

        with open('server_data/servers.yml') as data_file:
            self.servers = self.yaml.load(data_file)

        for i in self.servers.keys():
            if '{}.yml'.format(i) in os.listdir('server_data'):
                with open('server_data/{}.yml'.format(i)) as data_file:
                    data = self.yaml.load(data_file)
                    for key, s in data['queuetimer'].items():
                        if s != 'None' and s is not None:
                            data['queuetimer'][key] = datetime.timedelta(seconds=s)
                        elif s == 'None':
                            data['queuetimer'][key] = None
                            
                            
                    if 'words' not in data:
                        data['words'] = 10
                    if 'blacklist' not in data:
                        data['blacklist'] = True
                    self.server_data[i] = data

        with open('config.yml') as data_file:
            self.config = self.yaml.load(data_file)

        self.DEVELOPERS = self.config['ids']['developers']
        self.BOT_HOSTER = self.config['ids']['host']

        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        super().__init__(
            command_prefix=self.config['prefix'],
            command_not_found=HelperBodge('No command called `{}` found.'),
            *args,
            **kwargs
        )

    def save_data(self):
        with open('server_data/servers.yml', 'w') as data_file:
            self.yaml.dump(self.servers, data_file)
        for i in self.server_data.items():
            with open('server_data/{}.yml'.format(i[0]), 'w') as data_file:
                to_save = dict(i[1])
                queuetimer = dict(to_save['queuetimer'])
                for key, timedelta in queuetimer.items():
                    if timedelta != None:
                        queuetimer[key] = timedelta.total_seconds()
                to_save['queuetimer'] = queuetimer
                self.yaml.dump(to_save, data_file)
                
    def save_archive(self, sid):
        with open('./server_data/archive/{}-{}.yml'.format(sid, str(datetime.datetime.utcnow()).replace(':', '.')), 'w') as data_file:
            to_save = dict(self.server_data[sid])
            queuetimer = dict(to_save['queuetimer'])
            for key, timedelta in queuetimer.items():
                if timedelta != None:
                    queuetimer[key] = timedelta.total_seconds()
            to_save['queuetimer'] = queuetimer
            self.yaml.dump(to_save, data_file)

    async def send_message(self, to, msg):
        try:
            if len(msg) > 2000:
                await to.send('Whoops! Discord won\'t let me send messages over 2000 characters.\nThe message started with: ```\n{}```'.format(msg[:1000].replace('`', '`\u200b')))
            else:
                await to.send(msg)
            pass
        except discord.errors.Forbidden:
            pass

    async def on_message(self, message):
        await self.process_commands(message)

    async def process_commands_sudo(self, message):
        """|coro|
        This function processes the commands that have been registered
        to the bot and other groups. Without this coroutine, none of the
        commands will be triggered.
        By default, this coroutine is called inside the :func:`.on_message`
        event. If you choose to override the :func:`.on_message` event, then
        you should invoke this coroutine as well.
        This is built using other low level tools, and is equivalent to a
        call to :meth:`~.Bot.get_context` followed by a call to :meth:`~.Bot.invoke`.
        Parameters
        -----------
        message : discord.Message
            The message to process commands for.
        """
        ctx = await self.get_context(message)
        await self.invoke_sudo(ctx)
    
    async def invoke_sudo(self, ctx):
        """|coro|
        Invokes the command given under the invocation context and
        handles all the internal event dispatch mechanisms.
        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to invoke.
        """        
        if ctx.command is not None:
            self.dispatch('command', ctx)
            try:
                if 'no_sudo' not in [i.__qualname__.split('.')[0] for i in ctx.command.checks]:
                    vc = ctx.command._verify_checks
                    async def nvc(*args):
                        pass
                    ctx.command._verify_checks = nvc
                    await ctx.command.invoke(ctx)
                    ctx.command._verify_checks = vc
            except CommandError as e:
                print(e)
                await ctx.command.dispatch_error(ctx, e)
            else:
                self.dispatch('command_completion', ctx)
        elif ctx.invoked_with:
            exc = CommandNotFound('Command "{}" is not found'.format(ctx.invoked_with))
            self.dispatch('command_error', ctx, exc)
        
    
    async def notify_devs(self, lines, message: discord.Message = None):
        # form embed
        errorlog = self.get_channel(346011284346503168)
        if errorlog is None:
            self.logger.error('Could not find channel')
            return
        
        await errorlog.send('====================Start Error====================')
        if message is not None:
            await errorlog.send('==========Message triggering error==========')
            counter = 0
            while True:
                to_send = message.content[counter:counter+1900]
                if to_send:
                    await errorlog.send('```{}```'.format(to_send))
                    counter += 1900
                else:
                    break
            await errorlog.send('in channel {0} by {1}'.format(message.channel.id, message.author.name))

        await errorlog.send('{} UTC'.format(datetime.datetime.utcnow()))
        await errorlog.send('===============Error Message===============')
        error_message = ''.join(lines)
        counter = 0
        while True:
            to_send = error_message[counter:counter+1900]
            if to_send:
                await errorlog.send('```{}```'.format(to_send))
                counter += 1900
            else:
                break

        await errorlog.send('====================End Error====================')

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if isinstance(exception, commands.CommandInvokeError):
            # all exceptions are wrapped in CommandInvokeError if they are not a subclass of CommandError
            # you can access the original exception with .original
            if isinstance(exception.original, discord.Forbidden):
                # permissions error
                try:
                    await ctx.send('Permissions error: `{}`'.format(exception))
                except discord.Forbidden:
                    # we can't send messages in that channel
                    return

            # Print to log then notify developers
            lines = traceback.format_exception(type(exception),
                                               exception,
                                               exception.__traceback__)

            self.logger.error(''.join(lines))
            await self.notify_devs(lines, ctx.message)

            return
        
        if isinstance(exception, commands.CheckFailure):
            await ctx.send('You can\'t do that.')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data:
                await ctx.send('Error: {}'.format(' '.join(exception.args)))
            else:
                await ctx.send('Got to say, I *was* expecting `{1}` to be an `{0}`..'.format(*error_data[0]))
        else:
            info = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
            self.logger.error('Unhandled command exception - {}'.format(''.join(info)))
            await self.notify_devs(info, ctx.message)

    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        if isinstance(info[1], self.ErrorAlreadyShown):
            return
        await self.notify_devs(traceback.format_exception(*info, chain=False))

    async def on_ready(self):
        self.logger.info('Connected to Discord')
        self.logger.info('Guilds  : {}'.format(len(self.guilds)))
        self.logger.info('Users   : {}'.format(len(set(self.get_all_members()))))
        self.logger.info('Channels: {}'.format(len(list(self.get_all_channels()))))
        game = discord.Game(name='Type "{}how" for info on starting a miniTWOW!'.format(self.command_prefix))
        await self.change_presence(game=game)

    async def close(self):
        await super().close()

    def run(self):
        debug = any('debug' in arg.lower() for arg in sys.argv) or self.config.get('debug_mode', False)

        if debug:
            # if debugging is enabled, use the debug subconfiguration (if it exists)
            if 'debug' in self.config:
                self.config = {**self.config, **self.config['debug']}
            self.logger.info('Debug mode active...')
            self.debug = True

        token = self.config['token']
        cogs = self.config.get('cogs', [])
        self.remove_command("help")
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.exception('Failed to load cog {}.'.format(cog))
            else:
                self.logger.info('Loaded cog {}.'.format(cog))

        self.logger.info('Loaded {} cogs'.format(len(self.cogs)))
        super().run(token)

if __name__ == '__main__':
    bot = TWOWBot()
    bot.run()
