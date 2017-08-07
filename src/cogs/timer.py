import datetime
import asyncio

from discord.ext import commands
import discord

from cogs.util import checks, twow_helper, timed_funcs


class Timer():
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_timer())
        
    async def check_timer(self):
        await self.bot.wait_until_ready()

        while True:
            current_time = datetime.datetime.utcnow()
            for cid, sd in self.bot.server_data.items():
                round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                votetime = round['votetimer']
                restime = round['restimer']
                if type(votetime) == datetime.datetime and current_time > votetime:
                    asyncio.ensure_future(timed_funcs.start_voting(self.bot, self.bot.get_channel(cid)))
                elif type(restime) == datetime.datetime and current_time > restime:
                    channel = self.bot.get_channel(cid)
                    await timed_funcs.do_results(
                        self.bot, 
                        channel, 
                        channel.guild, 
                        '20%' #TODO make this an option
                    )
                    
            await asyncio.sleep(5)
    
            
    @commands.command(aliases=['settimes','settimer','set_timer'])
    @checks.twow_exists()
    @checks.is_twow_host()
    async def set_times(self, ctx, *times):
        '''Set timer for next events. Events are voting and results.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m]`
        '''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if len(times) == 0:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}set_times <times>`'.format(ctx.prefix))
            return
        
        deltas = [twow_helper.get_delta(s) for s in times]
        now = datetime.datetime.utcnow()
        if sd['voting']:
            round['restimer'] = now+deltas[0]
            await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours and {} minutes.'.format(deltas[0].days, deltas[0].seconds//3600, deltas[0].seconds//60%60))
        else:
            round['votetimer'] = now+deltas[0]
            await ctx.bot.send_message(ctx.channel,
                'Set voting in {} days {} hours and {} minutes.'.format(deltas[0].days, deltas[0].seconds//3600, deltas[0].seconds//60%60))
            if len(times) > 1:
                net = deltas[0]+deltas[1]
                round['restimer'] = now+net
                await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours and {} minutes.'.format(net.days, net.seconds//3600, net.seconds//60%60))
                
        ctx.bot.save_data()

        
def setup(bot):
    bot.add_cog(Timer(bot))
