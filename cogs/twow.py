import inspect
import string
import re

from discord.ext import commands
import ruamel.yaml as yaml
import discord

from cogs.util import twow_helper


class Host():
    @commands.command()
    async def id(self, ctx):
        '''Get the server ID used in voting.
        This was set when this channel was registered.
        '''
        if ctx.channel.id in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 
                'This mTWOW\'s identifier is `{}`'.format(ctx.bot.servers[ctx.channel.id]))
        else:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data. If this is an error, please contact {}.'.format(ctx.bot.get_user(BOT_HOSTER)))
            
    @commands.command()
    async def prompt(self, ctx):
        '''Get the current prompt.
        The host of this mTWOW can use `set_prompt` to set it.
        '''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if round['prompt'] is None:
            await ctx.bot.send_message(ctx.channel, 'There\'s no prompt set yet for this mTWOW.')
            return
        
        await ctx.bot.send_message(ctx.channel, 'The current prompt is:\n{}\n'.format(round['prompt'].decode('utf-8')))
        
    @commands.command()
    async def season(self, ctx):
        '''Get the current season number.'''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        await ctx.bot.send_message(ctx.channel, 'We are on season {}'.format(sd['season']))
        
    @commands.command()
    async def round(self, ctx):
        '''Get the current round number.'''
        if ctx.channel.id not in ctx.bot.servers:
            await ctx.bot.send_message(ctx.channel, 'There isn\'t an entry for this mTWOW in my data.')
            return
        
        sd = ctx.bot.server_data[ctx.channel.id]
        
        await ctx.bot.send_message(ctx.channel, 'We are on round {}'.format(sd['round']))
        
    @commands.command()
    async def vote(self, ctx, identifier:str = '', *responsel):
        '''Vote on the responses.
        This command will only work in DMs.
        *I think it makes me a hot dog. Not sure.*'''
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.message.delete()
            await ctx.bot.send_message(ctx.channel, 'Please only vote in DMs')
            return
        
        if not identifier:
            await ctx.bot.send_message(ctx.channel, 
                'Usage: `{0}vote <TWOW id> [vote]\nUse `{0}id` in the channel to get the id.'.format(ctx.prefix))
            return
        
        id = identifier
        
        s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}
        
        if id not in s_ids:
            await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(id.replace('`', '\\`')))
            return
        
        sd = ctx.bot.server_data[s_ids[id]]
        
        if not sd['voting']:
            await ctx.bot.send_message(ctx.channel, 'Voting hasn\'t started yet. Sorry.')
            return
        
        if 'season-{}'.format(sd['season']) not in sd['seasons']:
            sd['seasons']['season-{}'.format(sd['season'])] = {}
        if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
            sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
        
        round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
        
        if not responsel:  # New slides needed!
            if ctx.author.id not in round['slides']:
                success = twow_helper.create_slides(ctx.bot, round, ctx.author.id)
                if not success:
                    await ctx.bot.send_message(ctx.author, 'I don\'t have enough responses to formulate a slide. Sorry.')
                    return
            slide = round['slides'][ctx.author.id]
            
            m = '**Your slide is:**'
            for n, i in enumerate(slide):
                m += '\n:regional_indicator_{}: {}'.format(string.ascii_lowercase[n], round['responses'][i].decode())
                if len(m) > 1500:
                    await ctx.bot.send_message(ctx.channel,m)
                    m = ''
            if m:
                await ctx.bot.send_message(ctx.channel,m)
        else:
            id = identifier
            vote_str = ' '.join(responsel)
            if ctx.author.id not in round['slides']:
                await ctx.bot.send_message(ctx.author, 'You don\'t have a voting slide *to* vote on!\nUse `.vote {}` to generate one.'.format(id))
                return
                
            slide = round['slides'][ctx.author.id]
            to = string.ascii_uppercase[len(slide) - 1]
            regex = '[A-{}]{{{}}}'.format(to, len(slide))
            if not re.compile(regex).match(vote_str):
                await ctx.bot.send_message(ctx.author, 'Please vote for **every** item on your slide exactly **once**.')
                return
            
            if len(set(vote_str)) != len(vote_str):  # Check for repeats
                await ctx.bot.send_message(ctx.author, 'Please vote for **every** item on your slide exactly **once**.')
                return
            
            vote = list(vote_str)
            for n, i in enumerate(vote):
                vote[n] = slide[string.ascii_uppercase.index(i)]
            
            round['votes'].append({
                'voter': ctx.author.id,
                'vote': vote
            })
            
            del round['slides'][ctx.author.id]
            ctx.bot.save_data()
            
            await ctx.bot.send_message(ctx.channel, 'Thanks for voting!')
            
    @commands.command()
    async def respond(self, ctx, identifier:str = '', *responsel):
        '''Respond to the current prompt.
        You can get the channel identifier by using `id` in that channel.
        This command only works in DMs.
        *Probbly handles the controlling of my kitten army*
        '''
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.message.delete()
            await ctx.bot.send_message(ctx.channel, 'Please only respond in DMs')
            return
        
        if not responsel:
            await ctx.bot.send_message(ctx.channel, 
                'Usage: `{0}respond <TWOW id> <response>`\nUse `{0}id` in the channel to get the id.'.format(ctx.prefix))
            return
        
        
        response = ' '.join(responsel)
        success, response = twow_helper.respond(ctx.bot, identifier, ctx.author.id, response)
        if success == 1: 
            await ctx.bot.send_message(ctx.channel, 
                'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
        elif success == 3:
            await ctx.bot.send_message(ctx.channel, 'Voting has already started. Sorry.')
        elif success == 5:
            await ctx.bot.send_message(ctx.channel, 'There\'s no prompt.. How can you even?')
        elif success == 7:
            await ctx.bot.send_message(ctx.channel, 'You are unable to submit this round. Please wait for the next season.')
        elif success == 9:
            await ctx.bot.send_message(ctx.channel, 'That is a lot of characters. Why don\'t we tone it down a bit?')
        else:
            if success // 2 % 2 == 1: 
                await ctx.bot.send_message(ctx.channel, '**Warning! Overwriting current response!**')
            if success // 4 % 2 == 1: 
                await ctx.bot.send_message(ctx.channel, '**Warning! Your response looks to be over 10 words ({}).**\nThis can be ignored if you are playing a variation TWOW that doesn\'t have this limit'.format(len(response.split(' '))))
            if success // 8 % 2 == 1:
                await ctx.bot.send_message(ctx.channel, '**Due to rude words, your submission has been changed to:**\n{}'.format(response))
            await ctx.bot.send_message(ctx.channel, '**Submission recorded**')
            
    @commands.command()
    async def how(self, ctx):
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
        msg += '**`round`** and **`season`** will tell you the round and season number responcively.\n'
        msg += '**`id`** will get you the channel identifier for that mTWOW. This is needed when responding or voting.\n'
        msg += '\n**Getting help:**\n'
        msg += 'All off these commands, and more, are avaliable in the **`help`** command.\n'
        msg += 'If you want to invite the bot to your server, or join the official one, use **`about`**.\n'
        msg += 'If you are interested in hosting this bot for yourself, check the GitHub linked in the **`about`** command,\n'
        msg += 'or DM one of the developers (also in the **`about`** command).'
        await ctx.bot.send_message(ctx.channel, msg)

        
def setup(bot):
    bot.add_cog(Host())
