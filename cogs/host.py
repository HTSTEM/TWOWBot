import inspect
import asyncio

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import results, twow_helper


class Host():
    @commands.command()
    async def start_voting(self, ctx):
        '''Start voting..
        This will end responding and will allow people to use `vote`.
        '''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if sd['owner'] != ctx.author.id:
            return
        
        if sd['voting']:
            await ctx.bot.send_message(ctx.channel, 'Voting is already active.')
            return
        roundn = sd['round']
        seasonn = sd['season']
        if len(sd['seasons']['season-{}'.format(seasonn)]['rounds']['round-{}'.format(roundn)]['responses']) < 2:
            await ctx.bot.send_message(ctx.channel, 'There aren\'t enough responses to start voting. You need at least 2.')
            return
        
        sd['voting'] = True
        ctx.bot.save_data()
        await ctx.bot.send_message(ctx.channel, 'Voting has been activated.')
        return
    
    @commands.command()
    async def results(self, ctx, nums:str = '20%'):
        '''End this round and show results.
        `nums` is either a percentage denoted by `%` (for example `5%`),
        or it it a set number of people to elimintate this round.
        *Woah? Results. Let's hope I know how to calculate these.. Haha. I didn't.*
        '''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if sd['owner'] != ctx.author.id:
            return
        
        if not sd['voting']:
            await ctx.bot.send_message(ctx.channel, 'Voting hasn\'t even started yet...')
            return
        
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        voted_ons = set()
        for vote in round['votes']: voted_ons |= set(vote['vote'])
        print(set(round['responses']))
        print(voted_ons)
        if set(round['responses']) != voted_ons:
            await ctx.bot.send_message(ctx.channel, 'Not every response has been voted on yet!')
            return
        totals = results.count_votes(round, sd['alive'])
        
        msg = '**Results for round {}, season {}:**'.format(sd['round'], sd['season'])
        await ctx.message.delete()
        await ctx.bot.send_message(ctx.channel,msg)
        
        eliminated = []
        living = []
        
        elim = int(0.8 * len(totals))
        try:
            if nums[-1] == '%':
                elim = len(totals)*(100-int(nums[:-1]))//100
            else:
                elim = len(totals) - int(nums)
        except ValueError:
            await ctx.bot.send_message(ctx.channel, '{} doesn\'t look like a number to me.'.format(nums))
            return
            
        for msg, dead, uid, n in results.get_results(totals, elim, round):
            user = ctx.guild.get_member(uid)
            if user is not None:
                name = user.mention
            else:
                name = str(uid)
                
            if dead:
                if user.id in sd['alive']:
                    sd['alive'].remove(user.id)
                    eliminated.append((name, user))
                else:
                    living.append((name, user))
            
            await asyncio.sleep(len(totals) - n / 2)
            await ctx.bot.send_message(ctx.channel,msg.format(name)) 
            
        user = ctx.guild.get_member(totals[0]['name'])
        if user is not None:
            name = user.mention
        else:
            name = str(v['name'])
        msg = '{}\nThe winner was {}! Well done!'.format('=' * 50, name)
        await ctx.bot.send_message(ctx.channel,msg)  
        
        await ctx.bot.send_message(ctx.channel,
            'Sadly though, we have to say goodbye to {}.'.format(', '.join([i[0] for i in eliminated])))

        # Do all the round incrementing and stuff.
        if len(totals) - len(eliminated) <= 1:
            await ctx.bot.send_message(ctx.channel,'**This season has ended! The winner was {}!**'.format(name))
            sd['round'] = 1
            sd['season'] += 1
        else:
            sd['round'] += 1
            await ctx.bot.send_message(ctx.channel,'**We\'re now on round {}!**'.format(sd['round']))
            
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {'rounds':{}}
            sd['alive'] = []
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        sd['voting'] = False
        
        ctx.bot.save_data()
        
    @commands.command()
    async def responses(self, ctx, sid:str = ''):
        '''List all responses this round.
        This command will send the responses via DMs.
        '''
        id = None
        if sid:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            if sid not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(sid.replace('`', '\\`')))
                return
            id = s_ids[sid]
        else:
            if ctx.channel.id not in ctx.bot.servers:
                await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
                return
            id = ctx.channel.id
            
        if ctx.bot.server_data[id]['owner'] != ctx.author.id:
            return
            
        sd = ctx.bot.server_data[id]
        
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
                await ctx.bot.send_message(ctx.channel, 'Usage: `{}register <short identifier>'.format(ctx.prefix))
    
    @commands.command()
    async def show_config(self, ctx, sid:str = ''):
        '''Sends the config file for this channel.
        **WARNING!**
        This file contains everyone's responses, as well as their votes, so
        don't use this command out of DMs.
        '''
        id = None
        if sid:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
            if sid not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(sid.replace('`', '\\`')))
                return
            id = s_ids[sid]
        else:
            if ctx.channel.id not in ctx.bot.servers:
                await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
                return
            id = ctx.channel.id
            
        if ctx.bot.server_data[id]['owner'] != ctx.author.id:
            return
        
        with open('./server_data/{}.yml'.format(ctx.channel.id), 'rb') as server_file:
            await ctx.channel.send(file=discord.File(server_file))
            
    @commands.command()
    async def set_prompt(self, ctx, *promptl):
        '''Set the prompt for this round.
        *Summon unicorns*
        '''
        prompt = ' '.join(promptl)
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if sd['owner'] != ctx.author.id:
            return
        
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
            return
        else:
            await ctx.bot.send_message(ctx.channel, 'The prompt has been changed from `{}` to `{}` for this round.'.format(round['prompt'].decode('utf-8'), prompt.replace('@', '@\u200b').replace('`', '\\`')))
            round['prompt'] = prompt.replace('@', '@\u200b').replace('`', '\\`').encode('utf-8')
            ctx.bot.save_data()
            return
    
    @commands.command()
    async def transfer(self, ctx):
        '''Transfer ownership of this mTWOW.
        Do `transfer @mention`.
        '''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        if sd['owner'] != ctx.author.id:
            return
        
        if len(ctx.message.mentions) == 0:
            await ctx.bot.send_message(ctx.channel, 'Usage: `{}transfer <User>`'.format(PREFIX))
            return
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content[0].lower() in ['y','n']
        
        await ctx.bot.send_message(ctx.channel, 
            'You are about to transfer your mtwow to {}. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.'.format(ctx.message.mentions[0].name))
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
        await ctx.bot.send_message(ctx.channel, 'MTWOW has been transfered to {}.'.format(ctx.message.mentions[0].name))
        
    @commands.command()
    async def delete(self, ctx):
        '''Delete the mTWOW.
        An archive will be stored and can be located by the hoster of the bot.'''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        if sd['owner'] != ctx.author.id:
            return
        
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author and m.content[0].lower() in ['y','n']
        
        await ctx.bot.send_message(ctx.channel, 
            'You are about to delete your mtwow. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.')
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
        await ctx.bot.send_message(ctx.channel, 'MTWOW has been deleted.')
        
def setup(bot):
    bot.add_cog(Host())
