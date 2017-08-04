import datetime

from discord.ext import commands
import ruamel.yaml as yaml
import discord

class Core():

    @commands.command()
    async def help(self, ctx, *args):
        commands = {i for i in ctx.bot.all_commands.values()}

        '''commands = {
            'help':('[command]','get help on commands.'),
            'ping':('','ping the bot.'),
            'me':('','tells you about yourself.'),
            'about':('','about TWOWBot.'),
            'id':('','get the twow id of the current channel.'),
            'prompt':('','get the prompt of the current channel.'),
            'season':('','get the season of the current channel.'),
            'round':('','get the round of the current channel'),
            'respond':('<mtwow id> <response>','respond to a prompt.'),
            'vote':('<mtwow id> [vote]','vote on a mTWOW.'),
            'register':('<mtwow id>','registers the current channel with an id'),
            'show_config':('[mtwow id]','get the database for a channel.'),
            'responses':('[mtwow id]','get the responses for this round.'),
            'set_prompt':('<prompt>','set the prompt for the current channel.'),
            'start_voting':('','starts voting for the current channel.'),
            'results':('[elimination]','get the results for the current mTWOW. Specify elimination amount using a number or percentage using `%`. Defaults to 20%.'),
            'transfer':('<user>','transfer ownership of mtwow to someone else.'),
            'delete':('','delete the current mtwow.')
        }'''


        if len(args) == 0:
            d = '**TWOWBot help:**'

            for cmd in commands:
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

                params = list(cmd.clean_params.items())
                p_str = ''
                for p in params:
                    if p[1].default == p[1].empty:
                        p_str += ' [{}]'.format(p[0])
                    else:
                        p_str += ' <{}>'.format(p[0])

                d += '`{}{}{}`\n'.format(ctx.prefix, cmd.name, p_str)
                d += '\n**Description:**\n'
                d += '{}\n'.format(cmd.help)

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

        d += '\n*Made by Bottersnike#3605, hanss314#0128 and Noahkiq#0493*'
        await ctx.bot.send_message(ctx.channel, d)

    @commands.command()
    async def ping(self, ctx):
        await ctx.bot.send_message(ctx.channel, 'Pong!')

    @commands.command(aliases=['info'])
    async def about(self, ctx):
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

def setup(bot):
    bot.add_cog(Core())
