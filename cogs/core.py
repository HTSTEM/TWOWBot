import datetime

from discord.ext import commands
import ruamel.yaml as yaml
import discord

class Core():
    
    @commands.command()
    async def help(self, ctx, *args):
        commands = {
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
        }
        n = len(max(list(commands.keys()), key=lambda x:len(x)))
        
        d = '**TWOWBot help:**\n'
        
        if len(args) == 0:
            d += '\n'.join(['`{}{} {}` - {}'.format(ctx.prefix,i[0], i[1][0], i[1][1]) for i in commands.items()])
        else:            
            for i in args:
                if i in commands:
                    d += '`{}{} {}` - {}\n'.format(ctx.prefix, i, commands[i][0], commands[i][1])
                else:
                    d += '`{}{}` - Command not found\n'.format(ctx.prefix, i.replace('@', '@\u200b').replace('`', '`\u200b'))
            d = d[:-1]
            
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
