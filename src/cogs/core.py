import datetime

from discord.ext import commands
import discord

from .util.categories import category


class Core:
    @category('info')
    @commands.command()
    async def help(self, ctx, *args):
        '''This help message :D'''
        cmds = {i for i in ctx.bot.all_commands.values()}

        if len(args) == 0:
            d = ''#'**TWOWBot help:**'

            cats = {}
            for cmd in cmds:
                if not hasattr(cmd, 'category'):
                    cmd.category = 'Misc'
                if cmd.category not in cats:
                    cats[cmd.category] = []
                cats[cmd.category].append(cmd)

            d += '\n**Categories:**\n'
            for cat in cats:
                d += '**`{}`**\n'.format(cat)
            d += '\nUse `{}help <category>` to list commands in a category'.format(ctx.prefix)
            d += '\nUse `{}help <command>` to get indepth help for a command\n'.format(ctx.prefix)
        elif len(args) == 1:
            cats = {}
            for cmd in cmds:
                if not hasattr(cmd, 'category'):
                    cmd.category = 'Misc'
                if cmd.category not in cats:
                    cats[cmd.category] = []
                cats[cmd.category].append(cmd)
            if args[0].title() in cats:
                d = 'Commands in caterogy **`{}`**:\n'.format(args[0])
                for cmd in sorted(cats[args[0].title()], key=lambda x:x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Command not found.'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = 'Help for command `{}`:\n'.format(cmd.name)
                    d += '\n**Usage:**\n'

                    if type(cmd) != commands.core.Group:
                        params = list(cmd.clean_params.items())
                        p_str = ''
                        for p in params:
                            if p[1].default == p[1].empty:
                                p_str += ' [{}]'.format(p[0])
                            else:
                                p_str += ' <{}>'.format(p[0])
                        d += '`{}{}{}`\n'.format(ctx.prefix, cmd.name, p_str)
                    else:
                        d += '`{}{} '.format(ctx.prefix, cmd.name)
                        if cmd.invoke_without_command:
                            d += '['
                        else:
                            d += '<'
                        d += '|'.join(cmd.all_commands.keys())
                        if cmd.invoke_without_command:
                            d += ']`\n'
                        else:
                            d += '>`\n'
                    
                    d += '\n**Description:**\n'
                    d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

                    if cmd.aliases:
                        d += '\n**Aliases:**'
                        for alias in cmd.aliases:
                            d += '\n`{}{}`'.format(ctx.prefix, alias)

                        d += '\n'
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if hasattr(cmd, 'all_commands') and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    if cmd == ctx.bot:
                        d += 'Command not found.'
                    else:
                        d += '`{}` has no sub-command `{}`.'.format(cmd.name, i)
                    break
            if cmd != ctx.bot:
                d = 'Help for command `{}`:\n'.format(cmd_name)
                d += '\n**Usage:**\n'

                if type(cmd) != commands.core.Group:
                    params = list(cmd.clean_params.items())
                    p_str = ''
                    for p in params:
                        if p[1].default == p[1].empty:
                            p_str += ' [{}]'.format(p[0])
                        else:
                            p_str += ' <{}>'.format(p[0])
                    d += '`{}{}{}`\n'.format(ctx.prefix, cmd_name, p_str)
                else:
                    d += '`{}{} '.format(ctx.prefix, cmd.name)
                    if cmd.invoke_without_command:
                        d += '['
                    else:
                        d += '<'
                    d += '|'.join(cmd.all_commands.keys())
                    if cmd.invoke_without_command:
                        d += ']`\n'
                    else:
                        d += '>`\n'

                d += '\n**Description:**\n'
                d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

                if cmd.aliases:
                    d += '\n**Aliases:**'
                    for alias in cmd.aliases:
                        d += '\n`{}{}`'.format(ctx.prefix, alias)

                    d += '\n'
            '''
            d = '**TWOWBot help:**'

            for i in args:
                if i in ctx.bot.all_commands:
                    cmd = ctx.bot.all_commands[i]
                    d += '\n`{}{}`'.format(ctx.prefix, i)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is None:
                        brief = 'No description'

                    d += ' - {}'.format(brief)
                else:
                    d += '\n`{}{}` - Command not found'.format(ctx.prefix, i.replace('@', '@\u200b').replace('`', '`\u200b'))
            '''
        d += '\n*Made by Bottersnike#3605, hanss314#0128 and Noahkiq#0493*'
        await ctx.bot.send_message(ctx.channel, d)

    @category('info')
    @commands.command()
    async def ping(self, ctx):
        '''Ping the bot.'''
        await ctx.bot.send_message(ctx.channel, 'Pong!')

    @category('info')
    @commands.command(aliases=['info'])
    async def about(self, ctx):
        '''Get info about the bot.
        This is also where the invite link is avaliable from.
        '''
        mess = '**This bot was developed by:**\n'
        mess += 'Bottersnike#3605\n'
        mess += 'hanss314#0128\n'
        mess += 'Noahkiq#0493\n'
        mess += '\n**This bot is being hosted by:**\n'
        mess += '{}\n'.format(ctx.bot.get_user(ctx.bot.BOT_HOSTER))
        mess +='**\n(Official) TWOWBot\'s avatar by:**\n'
        mess += 'Imagine4#8208\n'
        mess += '\n**Resources:**\n'
        mess += '*The official TWOWBot discord server:* https://discord.gg/eZhpeMM\n'
        mess += '*Go contribute to TWOWBot on GitHub:* <https://github.com/HTSTEM/TWOW_Bot>\n'
        mess += '*Invite TWOWBot to your server:* <https://discordapp.com/oauth2/authorize?client_id={}&scope=bot>'.format(ctx.bot.user.id)
        await ctx.bot.send_message(ctx.channel, mess)

    @category('info')
    @commands.command(aliases=['aboutme','boutme','\'boutme'])
    @commands.guild_only()
    async def me(self, ctx):
        '''Get info about yourself.'''
        member = ctx.author
        now = datetime.datetime.utcnow()
        joined_days = now - member.joined_at
        created_days = now - member.created_at
        avatar = member.avatar_url

        embed = discord.Embed(colour=member.colour)
        embed.add_field(name='Nickname', value=member.display_name)
        embed.add_field(name='User ID', value=member.id)
        embed.add_field(name='Avatar', value='[Click here to show]({})'.format(avatar))

        embed.add_field(name='Created', value=member.created_at.strftime('%x %X') + '\n{} days ago'.format(max(0, created_days.days)))
        embed.add_field(name='Joined', value=member.joined_at.strftime('%x %X') + '\n{} days ago'.format(max(0, joined_days.days)))
        roles = '\n'.join([r.mention for r in sorted(member.roles, key=lambda x:x.position, reverse=True) if r.name != '@everyone'])
        if roles == '': roles = '\@everyone'
        embed.add_field(name='Roles', value=roles)

        embed.set_author(name=member, icon_url=avatar)

        try:
            await ctx.channel.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        
        
    @category('info')
    @commands.command(aliases=['instructions'])
    async def how(self, ctx):
        '''Get instructions on hosting a mTWOW.'''
        msg  = '**Hosting a mTWOW:**\n'
        msg += 'The host of a mTWOW has a couple of commands for them to use:\n'
        msg += '**`set_prompt`** will set the prompt for the round.\n'
        msg += '**`responses`** will send you a DM listing all of the responses so far.\n'
        msg += '**`start_voting`** will then close responses and allow people to vote.\n'
        msg += 'Finally, **`results`** will end the round and show results\n'
        msg += 'You can also use **`transfer`** to make someone else the host of the mTWOW.\n'
        
        msg += '\n**Traditional mTWOWs:**\n'
        msg += 'The owner of a mTWOW can setup a traditional mTWOW where anyone can host:\n'
        msg += '**`can_queue on`** will allow people to join the hosting queue with **`join_queue`**.\n'
        msg += '**`queue_timer`** will allow you to set a timer for the events.\n'
        msg += 'Use **`help queue_timer`** and **`help set_timer`** help on the timer.\n'
        msg += '**`skip_host`** will skip the current host and start a fresh season.\n'
        
        msg += '\n**Participating in a mTWOW:**\n'
        msg += 'When you are participating, you also have some commands you can use:\n'
        msg += '**`respond`**, when in a DM, allows you to respond to a prompt.\n'
        msg += '**`vote`**, when in a DM, will first generate your voting slide, and then allow you to vote on it.\n'
        
        msg += '\n**Other useful commands:**\n'
        msg += 'There are a few commands that are useful to know:\n'
        msg += '**`prompt`** will show you the current prompt.\n'
        msg += '**`round`** and **`season`** will tell you the round and season number respectively.\n'
        msg += '**`status`** and **`season`** will give you information about a mTWOW.\n'
        msg += '**`id`** will get you the channel identifier for that mTWOW. This is needed when responding or voting.\n'
        
        msg += '\n**Getting help:**\n'
        msg += 'All off these commands, and more, are avaliable in the **`help`** command.\n'
        msg += 'If you want to invite the bot to your server, or join the official one, use **`about`**.\n'
        msg += 'If you are interested in hosting this bot for yourself, check the GitHub linked in the **`about`** command,\n'
        msg += 'or DM one of the developers (also in the **`about`** command).'
        
        await ctx.bot.send_message(ctx.author, msg)
        await ctx.bot.send_message(ctx, ':mailbox_with_mail:')

def setup(bot):
    bot.add_cog(Core())
