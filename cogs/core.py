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

def setup(bot):
    bot.add_cog(Core())
