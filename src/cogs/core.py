import datetime

from discord.ext import commands
import ruamel.yaml as yaml
import discord

class Core():

    @commands.command()
    async def help(self, ctx, *args):
        '''This help message :D'''
        cmds = {i for i in ctx.bot.all_commands.values()}

        if len(args) == 0:
            d = '**TWOWBot help:**'

            for cmd in cmds:
                d += '\n`{}{}`'.format(ctx.prefix, cmd.name)

                brief = cmd.brief
                if brief is None and cmd.help is not None:
                    brief = cmd.help.split('\n')[0]

                if brief is not None:
                    d += ' - {}'.format(brief)
        elif len(args) == 1:
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

                if cmd.checks:
                    d += '\n**Checks:**'
                    for check in cmd.checks:
                        d += '\n{}'.format(check.__qualname__.split('.')[0])
                    d += '\n'

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

                if cmd.checks:
                    d += '\n**Checks:**'
                    for check in cmd.checks:
                        d += '\n{}'.format(check.__qualname__.split('.')[0])
                    d += '\n'

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

    @commands.command()
    async def ping(self, ctx):
        '''Ping the bot.'''
        await ctx.bot.send_message(ctx.channel, 'Pong!')

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
        #mess +='**\nTWOWBot\'s avatar by:**\n'
        #mess += 'name#discrim\n'
        mess += '\n**Resources:**\n'
        mess += '*The official TWOWBot discord server:* https://discord.gg/eZhpeMM\n'
        mess += '*Go contribute to TWOWBot on GitHub:* https://github.com/HTSTEM/TWOW_Bot\n'
        mess += '*Invite TWOWBot to your server:* <https://discordapp.com/oauth2/authorize?client_id={}&scope=bot>'.format(ctx.bot.user.id)
        await ctx.bot.send_message(ctx.channel, mess)

    @commands.command(aliases=['aboutme','boutme','\'boutme'])
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
        
    @commands.command(aliases=['instructions'])
    async def how(self, ctx):
        '''Get instructions on hosting a mTWOW.'''
        msg  = '**Hosting an mTWOW:**\n'
        msg += 'The host of an mTWOW has a coupple of commands for them to use:\n'
        msg += '**`set_prompt`** will set the prompt for the round.\n'
        msg += '**`responses`** will send you a DM listing all of the responses so far.\n'
        msg += '**`start_voting`** will then close responses and allow people to vote.\n'
        msg += 'Finally, **`results`** will end the round and show results\n'
        msg += 'You can also use **`transfer`** to make someone else the host of the mTWOW.\n'
        msg += '\n**Participating in an mTWOW:**\n'
        msg += 'When you are participating, you also have some commands you can use:\n'
        msg += '**`respond`**, when in a DM, allows you to respond to a prompt.\n'
        msg += '**`vote`**, when in a DM, will first generate your voting slide, and then allow you to vote on it.\n'
        msg += '\n**Other useful commands:**\n'
        msg += 'There are a few commands that are useful to know:\n'
        msg += '**`prompt`** will show you the current prompt.\n'
        msg += '**`round`** and **`season`** will tell you the round and season number respectively.\n'
        msg += '**`id`** will get you the channel identifier for that mTWOW. This is needed when responding or voting.\n'
        msg += '\n**Getting help:**\n'
        msg += 'All off these commands, and more, are avaliable in the **`help`** command.\n'
        msg += 'If you want to invite the bot to your server, or join the official one, use **`about`**.\n'
        msg += 'If you are interested in hosting this bot for yourself, check the GitHub linked in the **`about`** command,\n'
        msg += 'or DM one of the developers (also in the **`about`** command).'
        await ctx.bot.send_message(ctx.channel, msg)

def setup(bot):
    bot.add_cog(Core())
