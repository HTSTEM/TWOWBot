import datetime
import inspect
import asyncio

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import results, twow_helper, checks, timed_funcs


class Host():
    @commands.command(aliases=['startvoting'])
    @checks.twow_exists()
    @checks.is_twow_host()
    async def start_voting(self, ctx):
        '''Start voting..
        This will end responding and will allow people to use `vote`.
        '''
        
        await timed_funcs.start_voting(ctx.bot, ctx.channel)
        return
    
    @commands.command()
    @checks.twow_exists()
    @checks.is_twow_host()
    async def results(self, ctx, nums:str = '20%'):
        '''End this round and show results.
        `nums` is either a percentage denoted by `%` (for example `5%`),
        or it it a set number of people to elimintate this round.
        *Woah? Results. Let's hope I know how to calculate these.. Haha. I didn't.*
        '''

        await timed_funcs.do_results(ctx.bot, ctx.channel, ctx.guild, nums, message=ctx.message)
        return
        
    @commands.command()
    async def responses(self, ctx, identifier:str = ''):
        '''List all responses this round.
        This command will send the responses via DMs.
        '''
        id = None
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            
            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return
            
            id = s_ids[identifier]
        else:
            if ctx.channel.id not in ctx.bot.server_data:
                await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
                return
        
            id = ctx.channel.id
        
        sd = ctx.bot.server_data[id]
        
        if sd['owner'] != ctx.author.id:
            return
        
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        m = '**Responses for season {}, round {} so far:**'.format(sd['season'], sd['round'])
        for i in round['responses'].items():
            u = ctx.bot.get_user(i[0])
            if u is not None:
                n = u.name
            else:
                n = i[0]
            m += '\n**{}**: {}'.format(n, i[1].decode('utf-8'))
            if len(m) > 1500:
                await ctx.bot.send_message(ctx.author,m)
                m = ''
        if m:
            await ctx.bot.send_message(ctx.author,m)
        if isinstance(ctx.channel, discord.TextChannel):
            await ctx.bot.send_message(ctx.channel,':mailbox_with_mail:')
    
    @commands.command(aliases=['del_response', 'rem_response', 'delresponse', 'remresponse'])
    async def remove_response(self, ctx, identifier:str, respondee:str):
        '''Removes a response that has been submitted.
        `respondee` must be the exact name as shown in `responses`.
        A message is sent to the channel running the mTWOW, so be prepared
        to defend your reasoning.
        '''
    
        s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
        if identifier not in s_ids:
            await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
            return
        id = s_ids[identifier]
        sd = ctx.bot.server_data[id]
        
        if sd['owner'] != ctx.author.id:
            return
        
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        for i in round['responses'].items():
            u = ctx.bot.get_user(i[0])
            if u is not None:
                n = u.name
            else:
                n = i[0]
            if n.lower() == respondee.lower():
                break
        else:
            await ctx.bot.send_message(ctx.channel, '`{}` doesn\'t appear to have responded.'.format(respondee.replace('`', '\\`')))
            return
        
        await ctx.bot.send_message(ctx.channel, '<@{}>s response of {} has been removed.'.format(u.id, i[1].decode('utf-8')))
        del round['responses'][i[0]]
        chan = ctx.bot.get_channel(id)
        if chan:
            await ctx.bot.send_message(chan, '<@{}>, your response has been removed by <@{}>.'.format(u.id, sd['owner']))
        
        ctx.bot.save_data()
        
    
    @commands.command()
    async def register(self, ctx, identifier:str = ''):
        '''Setup channel initially
        Do all the fancy stuff to get this channel ready to host a mTWOW!
        '''
        if ctx.channel.id in ctx.bot.servers:
            owner = ctx.bot.get_user(ctx.bot.server_data[ctx.channel.id]['owner'])
            if owner is not None:
                await ctx.bot.send_message(ctx.channel, 'This channel is already setup. The owner is {}.'.format(owner.name.replace('@', '@\u200b')))
            else:
                await ctx.bot.send_message(ctx.channel, 
                    'I can\'t find the owner of this mTWOW. Please contact {} to resolve this.'.format(ctx.bot.get_user(BOT_HOSTER)))
        else:
            if not ctx.channel.permissions_for(ctx.author).manage_channels:#if user can manage that channel. CHANGE THIS
                return
            bot_perms = ctx.channel.permissions_for(ctx.guild.get_member(ctx.bot.user.id))
            if not (bot_perms.send_messages and bot_perms.read_messages): #add any other perms you can think of
                return
            if identifier:
                if ' ' in identifier:
                    await ctx.bot.send_message(ctx.channel, 'No spaces in the identifier please')
                    return
                if identifier in list(ctx.bot.servers.values()):
                    await ctx.bot.send_message(ctx.channel, 'There\'s already a mTWOW setup with that name. Sorry.')
                    return
                
                twow_helper.new_twow(ctx.bot, identifier, ctx.channel.id, ctx.author.id)
            
                await ctx.bot.send_message(ctx.channel, 
                    'Woah! I just set up a whole mTWOW for you under the name `{}`'.format(
                        identifier.replace('@', '@\u200b').replace('`', '\\`')))
            else:
                await ctx.bot.send_message(ctx.channel, 'Usage: `{}register <short identifier>`'.format(ctx.prefix))
    
    @commands.command()
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def show_config(self, ctx, identifier:str = ''):
        '''Sends the config file for this channel.
        **WARNING!**
        This file contains everyone's responses, as well as their votes, so
        don't use this command out of DMs.
        '''
        id = None
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            id = s_ids[identifier]
        else:
            id = ctx.channel.id
        
        with open('./server_data/{}.yml'.format(ctx.channel.id), 'rb') as server_file:
            await ctx.author.send(file=discord.File(server_file))
            
    @commands.command(aliases=['setelim'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def set_elim(self, ctx, amount):
        '''Sets the default elimination threshold.
        Use a number to specify number of contestants, e.g. `3`
        Add a percentage to specify percentage of contestants, e.g. `20%`
        '''
        try:
            if amount[-1] == '%': _ = int(amount[:-1])
            else: _ = int(amount)
        except ValueError:
            ctx.bot.send_message(ctx.channel, '{} is not in a valid format.'.format(amount))
            return
            
        sd = ctx.bot.server_data[ctx.channel.id]
        sd['elim'] = amount
        await ctx.bot.send_message(ctx.channel, 'Set elimination threshold to {}.'.format(amount))
        ctx.bot.save_data()
            
    @commands.command(aliases=['skiphost'])
    @checks.twow_exists()
    @checks.can_queue()
    @checks.is_twow_host()
    async def skip_host(self, ctx):
        '''Skip to next host'''
        sd = ctx.bot.server_data[ctx.channel.id]
        await twow_helper.next_host(ctx.bot, ctx.channel, sd)

    @commands.command(aliases=['setprompt'])
    @checks.twow_exists()
    @checks.is_twow_host()
    async def set_prompt(self, ctx, *promptl):
        '''Set the prompt for this round.
        *Summon unicorns*
        '''
        prompt = ' '.join(promptl)
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        # If you're someone who likes all code to look pristine, I appologise for the next few lines :'(
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if round['prompt'] is None:
            round['prompt'] = prompt.replace('@', '@\u200b').replace('`', '\\`').encode('utf-8')
            ctx.bot.save_data()
            await ctx.bot.send_message(ctx.channel, 'The prompt has been set to `{}` for this round.'.format(prompt.replace('@', '@\u200b').replace('`', '\\`')))
            if sd['queuetimer']['voting'] != None:
                round['votetimer'] = datetime.datetime.utcnow()+sd['queuetimer']['voting']
            return
        else:
            await ctx.bot.send_message(ctx.channel, 'The prompt has been changed from `{}` to `{}` for this round.'.format(round['prompt'].decode('utf-8'), prompt.replace('@', '@\u200b').replace('`', '\\`')))
            round['prompt'] = prompt.replace('@', '@\u200b').replace('`', '\\`').encode('utf-8')
            ctx.bot.save_data()
            return

    @commands.command(aliases=['setwords'])
    @checks.twow_exists()
    @checks.is_twow_host()
    async def set_words(self, ctx, words:int):
        '''Set the maximum words for a response.'''
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if words > 0:
            await ctx.bot.send_message(ctx.channel, 'The word limit has been set to {}.'.format(words))
            sd['words'] = words
        else:
            await ctx.bot.send_message(ctx.channel, 'The word limit has been removed.')
            sd['words'] = 0
        ctx.bot.save_data()
        
    @commands.group(pass_context=True, invoke_without_command=True)
    @checks.twow_exists()
    async def blacklist(self, ctx):
        '''Are rude words banned?'''
        sd = ctx.bot.server_data[ctx.channel.id]
        if sd['blacklist']:
            await ctx.bot.send_message(ctx.channel, 'The blacklist is **enabled**.')
        else:
            await ctx.bot.send_message(ctx.channel, 'The blacklist is **dissabled**.')
        
    @blacklist.command(pass_context=True, aliases=['enable'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def on(ctx):
        '''Enable the blacklist'''
        sd = ctx.bot.server_data[ctx.channel.id]
        sd['blacklist'] = True
        await ctx.bot.send_message(ctx.channel, 'The blacklist has been **enabled** for this mTWOW.')
        ctx.bot.save_data()
    
    @blacklist.command(pass_context=True, aliases=['dissable'])
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def off(ctx):
        '''Dissable the blacklist'''
        sd = ctx.bot.server_data[ctx.channel.id]
        sd['blacklist'] = False
        await ctx.bot.send_message(ctx.channel, 'The blacklist has been **dissabled** for this mTWOW.')
        ctx.bot.save_data()
        
    @commands.group(aliases=['canqueue'], pass_context=True, invoke_without_command=True)
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def can_queue(self, ctx):
        '''Sets if there is a hosting queue. There is none by default'''
        pass
                
    @can_queue.command(pass_context=True)
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def on(self, ctx):
        '''Allows queue'''
        sd = ctx.bot.server_data[ctx.channel.id]
        sd['canqueue'] = True
        await ctx.bot.send_message(ctx.channel, 'Anyone can now host in this channel!')
        ctx.bot.save_data()
        
    @can_queue.command(pass_context=True)
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def off(self, ctx):
        '''Disallows queue'''
        sd = ctx.bot.server_data[ctx.channel.id]
        sd['canqueue'] = False
        sd['queue'] = []
        await ctx.bot.send_message(ctx.channel, 'Only the owner can now host in this channel!')
        ctx.bot.save_data()
        
    @commands.command(aliases=['joinqueue'])
    @checks.can_queue()
    async def join_queue(self, ctx):
        '''Puts yourself in queue for hosting.'''
        sd = ctx.bot.server_data[ctx.channel.id]
        queue = sd['queue']
        if ctx.author.id in queue:
            await ctx.bot.send_message(ctx.channel, 'You are already in the queue!')
        else:
            queue.append(ctx.author.id)
            await ctx.bot.send_message(ctx.channel, 'You have been added to the hosting queue.')
            if len(ctx.bot.server_data[ctx.channel.id]['queue']) == 1:
                if sd['queuetimer']['prompt'] != None:
                    import datetime
                    sd['hosttimer'] = datetime.datetime.utcnow()+sd['queuetimer']['prompt']
                name = ctx.author.mention
                await ctx.bot.send_message(ctx.channel, '{} is now hosting!'.format(name))
            ctx.bot.save_data()

    @commands.command()
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def transfer(self, ctx):
        '''Transfer ownership of this mTWOW.
        Do `transfer @mention`.
        '''
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if len(ctx.message.mentions) != 1:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}transfer <User>`'.format(ctx.prefix))
            return
        
        if ctx.message.mentions[0].bot:
            await ctx.bot.send_message(ctx.channel, 'Haha, funny. Nice try kid.')
            return
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content[0].lower() in ['y','n']
        
        await ctx.bot.send_message(ctx.channel, 
            'You are about to transfer your mTWOW to {}. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.'.format(ctx.message.mentions[0].name))
        resp = None
        try:
            resp = await ctx.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.bot.send_message(ctx.channel, 'Transfer Cancelled.')
            return
        
        if resp.content[0].lower() != 'y':
            await ctx.bot.send_message(ctx.channel, 'Transfer Cancelled.')
            return

        sd['owner'] = ctx.message.mentions[0].id
        ctx.bot.save_data()
        await ctx.bot.send_message(ctx.channel, 'mTWOW has been transfered to {}.'.format(ctx.message.mentions[0].name))
        
    @commands.command()
    @checks.twow_exists()
    @checks.is_twow_owner()
    async def delete(self, ctx):
        '''Delete the mTWOW.
        An archive will be stored and can be located by the hoster of the bot.'''
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content[0].lower() in ['y','n']
        
        await ctx.bot.send_message(ctx.channel, 
            'You are about to delete your mTWOW. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.')
        resp = None
        try:
            resp = await ctx.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.bot.send_message(ctx.channel, 'Deletion Cancelled.')
            return
        
        if resp.content[0].lower() != 'y':
            await ctx.bot.send_message(ctx.channel, 'Deletion Cancelled.')
            return
        
        ctx.bot.save_archive(ctx.channel.id)
        ctx.bot.servers.pop(ctx.channel.id, None)
        ctx.bot.server_data.pop(ctx.channel.id,None)
        ctx.bot.save_data()
        await ctx.bot.send_message(ctx.channel, 'mTWOW has been deleted.')
        
def setup(bot):
    bot.add_cog(Host())
