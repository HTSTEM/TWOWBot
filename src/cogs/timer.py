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
                    if votetime != 'waiting':
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
    @checks.is_twow_owner()
    async def set_times(self, ctx, *times: twow_helper.get_delta):
        '''Set timer for next events. Events are voting and results.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m][<seconds>s]`
        '''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if len(times) == 0:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}set_times <times>`'.format(ctx.prefix))
            return
        
        now = datetime.datetime.utcnow()
        if sd['voting']:
            round['restimer'] = now+times[0]
            await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours {} minutes and {} seconds.'.format(
                    times[0].days, times[0].seconds//3600, times[0].seconds//60%60, times[0].seconds//60%60))
        else:
            round['votetimer'] = now+times[0]
            await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours {} minutes and {} seconds.'.format(
                    times[0].days, times[0].seconds//3600, times[0].seconds//60%60, times[0].seconds%60))
            if len(times) > 1:
                net = times[0]+times[1]
                round['restimer'] = now+net
                await ctx.bot.send_message(ctx.channel,
                'Set results in {} days {} hours {} minutes and {} seconds.'.format(
                    net.days, net.seconds//3600, net.seconds//60%60, net.seconds%60))
                
        ctx.bot.save_data()
        
    @commands.command(aliases=['queuetimes','queuetimer','queue_timer'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def queue_times(self, ctx, prompt_timeout: twow_helper.get_delta, 
      votetimer: twow_helper.get_delta, resultstimer: twow_helper.get_delta):
        '''Set timer for queue events.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m][<seconds>s]`
        '''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        print(prompt_timeout)
        print(votetimer)
        print(resultstimer)

        
def setup(bot):
    bot.add_cog(Timer(bot))
