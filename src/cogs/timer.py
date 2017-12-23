import datetime
import asyncio

from discord.ext import commands

from .util import checks, twow_helper, timed_funcs
from .util.categories import category


class Timer():
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.check_timer())
        
    async def check_timer(self):
        await self.bot.wait_until_ready()

        while True:
            current_time = datetime.datetime.utcnow()
            for cid, sd in self.bot.server_data.items():
                try:
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]

                    votetime = round['votetimer']
                    restime = round['restimer']
                    if isinstance(votetime, datetime.datetime) and current_time > votetime:
                        asyncio.ensure_future(timed_funcs.start_voting(self.bot, self.bot.get_channel(cid)))
                    elif isinstance(restime, datetime.datetime) and current_time > restime:
                        if votetime != 'waiting':
                            channel = self.bot.get_channel(cid)
                            asyncio.ensure_future(timed_funcs.do_results(
                                self.bot,
                                channel,
                                channel.guild,
                                sd['elim']
                            ))
                    elif (sd['canqueue'] and round['prompt'] == None and
                      type(sd['hosttimer']) == datetime.datetime and sd['hosttimer'] < current_time):
                        channel = self.bot.get_channel(cid)
                        asyncio.ensure_future(twow_helper.next_host(self.bot, channel, sd))

                except Exception as e:
                    import traceback
                    mess = traceback.format_exception(
                        type(e),
                        e,
                        e.__traceback__
                    )
                    self.bot.logger.error(mess)
                    await self.bot.notify_devs(mess)
                    continue
            
            await asyncio.sleep(5)
    
    @category('hosting')        
    @commands.command(aliases=['settimes','settimer','set_timer'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def set_times(self, ctx, *times: twow_helper.get_delta):
        '''Set timer for next events for this round. Events are voting and results.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m][<seconds>s]`
        '''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if len(times) == 0:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}set_times <times>`'.format(ctx.prefix))
            return
        
        now = datetime.datetime.utcnow()
        if sd['voting']:
            round['restimer'] = now+times[0] if times[0] else None
            await ctx.bot.send_message(ctx.channel,
                'Set results in {}.'.format(delta_to_string(times[0])))
        else:
            round['votetimer'] = now+times[0] if times[0] else None
            d = 'Set voting in {}. '.format(delta_to_string(times[0]))
            if len(times) > 1:
                net = times[0]
                if times[1]:
                    net += times[1]
                    round['restimer'] = now+net
                d += 'Set results in {}.'.format(delta_to_string(net))
            await ctx.bot.send_message(ctx.channel, d)
                
        ctx.bot.save_data()
    
    @category('hosting')
    @commands.command(aliases=['queuetimes','queuetimer','queue_timer'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def queue_times(self, ctx, prompt_timeout: twow_helper.get_delta=0, 
      votetimer: twow_helper.get_delta=0, resultstimer: twow_helper.get_delta=0):
        '''Set timer for queue events. These will timers will come into effect each round.
        If prompt_timeout is reached and the hoster has not created a prompt, they will be skipped.
        Time is specified in the format `[<days>d][<hours>h][<minutes>m][<seconds>s]`
        '''
        timers = ctx.bot.server_data[ctx.channel.id]['queuetimer']
        timers['prompt'] = prompt_timeout if prompt_timeout else None
        timers['voting'] = votetimer if votetimer else None
        timers['results'] = resultstimer if resultstimer else None
        ctx.bot.save_data()
        await ctx.bot.send_message(ctx.channel, 
            'The host will have {} to make a prompt, the contestants will have {} to respond and the voters will have {} to vote.'
            .format(delta_to_string(prompt_timeout),delta_to_string(votetimer),delta_to_string(resultstimer)))
        
def delta_to_string(delta):
    if not delta: return 'unlimited time'
    days = delta.days
    hours = delta.seconds//3600%60
    minutes = delta.seconds//60%60
    seconds = delta.seconds%60
    strings = []
    if days == 1: strings.append('1 day')
    elif days: strings.append('{} days'.format(days))
    
    if hours == 1: strings.append('1 hour')
    elif hours: strings.append('{} hours'.format(hours))
    
    if minutes == 1: strings.append('1 minute')
    elif minutes: strings.append('{} minutes'.format(minutes))
    
    if seconds == 1: strings.append('1 second')
    elif seconds or not strings: strings.append('{} seconds'.format(seconds))
    
    if len(strings)==1: return strings[0]
    else: return ' '.join(strings[:-1])+' and '+strings[-1]

        
def setup(bot):
    bot.add_cog(Timer(bot))
