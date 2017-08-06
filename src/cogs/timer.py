import datetime

from discord.ext import commands
import discord

from cogs.util import checks, twow_helper


class Timer():            
    @commands.command(aliases=['settimes','settimer','set_timer'])
    @checks.twow_exists()
    @checks.is_twow_host()
    async def set_times(self, ctx, *timel):
        '''Set timer for next events. Events are voting and results.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m]`
        '''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if len(timel) == 0:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}set_times <times>`'.format(ctx.prefix))
            return
        
        deltas = [twow_helper.get_delta(s) for s in timel]
        now = datetime.datetime.utcnow()
        if sd['voting']:
            round['restimer'] = str(now+deltas[0])
            await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours and {} minutes.'.format(deltas[0].days, deltas[0].seconds//3600, deltas[0].seconds//60%60))
        else:
            round['votetimer'] = str(now+deltas[0])
            await ctx.bot.send_message(ctx.channel,
                'Set voting in {} days {} hours and {} minutes.'.format(deltas[0].days, deltas[0].seconds//3600, deltas[0].seconds//60%60))
            if len(timel) > 1:
                net = deltas[0]+deltas[1]
                round['restimer'] = str(now+net)
                await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours and {} minutes.'.format(net.days, net.seconds//3600, net.seconds//60%60))
                
        ctx.bot.save_data()

        
def setup(bot):
    bot.add_cog(Timer())
