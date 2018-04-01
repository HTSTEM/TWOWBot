import string
import re
import datetime

from discord.ext import commands
import discord

from .util import twow_helper, checks, timed_funcs
from .util.categories import category
from .timer import delta_to_string


class TWOW:
    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def id(self, ctx):
        '''Get the server ID used in voting.
        This was set when this channel was registered.
        '''
        await ctx.bot.send_message(ctx.channel,
            'This mTWOW\'s identifier is `{}`'.format(ctx.bot.servers[ctx.channel.id]))

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def prompt(self, ctx, identifier:str = ''):
        '''Get the current prompt.
        The host of this mTWOW can use `set_prompt` to set it.
        '''
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}

            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return

            sd = ctx.bot.server_data[s_ids[identifier]]
        else:
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

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def season(self, ctx, identifier:str = ''):
        '''Get the current season number.'''
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}

            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return

            sd = ctx.bot.server_data[s_ids[identifier]]
        else:
            sd = ctx.bot.server_data[ctx.channel.id]

        await ctx.bot.send_message(ctx.channel, 'We are on season {}'.format(sd['season']))

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def round(self, ctx, identifier:str = ''):
        '''Get the current round number.'''
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}

            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return

            sd = ctx.bot.server_data[s_ids[identifier]]
        else:
            sd = ctx.bot.server_data[ctx.channel.id]

        await ctx.bot.send_message(ctx.channel, 'We are on round {}'.format(sd['round']))

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    @checks.in_twow()
    async def vote(self, ctx, identifier:str='', *, response=''):
        '''Vote on the responses.
        This command will only work in DMs.
        *I think it makes me a hot dog. Not sure.*'''
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            try: await ctx.message.delete()
            except discord.errors.Forbidden: pass
            await ctx.bot.send_message(ctx.channel, 'Please only vote in DMs')
            return

        if not identifier:
            await ctx.bot.send_message(ctx.channel,
                'Usage: `{0}vote <TWOW id> [vote]`\nUse `{0}id` in the channel to get the id.'.format(ctx.prefix))
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

        if not response:  # New slides needed!
            if ctx.author.id not in round['slides']:
                success = twow_helper.create_slides(ctx.bot, round, ctx.author.id, sd.get('self_voting'))
                if not success:
                    await ctx.bot.send_message(ctx.author, 'I don\'t have enough responses to formulate a slide. Sorry.')
                    return
            slide = round['slides'][ctx.author.id]

            m = '**Your slide is:**'
            for n, i in enumerate(slide):
                m += '\n:regional_indicator_{0}: {2} **({1})**'.format(string.ascii_lowercase[n], len(round['responses'][i].decode().split(' ')), round['responses'][i].decode())
                if len(m) > 1500:
                    await ctx.bot.send_message(ctx.channel,m)
                    m = ''
            if m:
                await ctx.bot.send_message(ctx.channel,m)
        else:
            id = identifier
            vote_str = response.upper()
            if ctx.author.id not in round['slides']:
                await ctx.bot.send_message(ctx.author, ':triumph: You don\'t have a voting slide *to* vote on!\nUse `.vote {}` to generate one.'.format(id))
                return

            slide = round['slides'][ctx.author.id]
            to = string.ascii_uppercase[len(slide) - 1]
            regex = '[A-{}]{{{}}}'.format(to, len(slide))
            if not re.compile(regex).match(vote_str):
                await ctx.bot.send_message(ctx.author, ':triumph: Please vote for **every** item on your slide exactly **once**.')
                return

            if len(set(vote_str)) != len(vote_str):  # Check for repeats
                await ctx.bot.send_message(ctx.author, ':triumph: Please vote for **every** item on your slide exactly **once**.')
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
            await ctx.bot.send_message(ctx.channel, ':ballot_box: Thanks for voting!')

            if round['restimer'] == 'waiting':
                voted_ons = set()
                for vote in round['votes']: voted_ons |= set(vote['vote'])
                if set(round['responses']) == voted_ons:
                    channel = ctx.bot.get_channel(s_ids[id])
                    await timed_funcs.do_results(
                        ctx.bot,
                        channel,
                        channel.guild,
                        '20%' #TODO make this an option
                    )

    @category('twow')
    @commands.command(aliases=['submit'])
    @checks.twow_exists()
    @checks.in_twow()
    async def respond(self, ctx, identifier:str = '', *, response):
        '''Respond to the current prompt.
        You can get the channel identifier by using `id` in that channel.
        This command only works in DMs.
        *Probably handles the controlling of my kitten army*
        '''
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            try: await ctx.message.delete()
            except discord.errors.Forbidden: pass
            await ctx.bot.send_message(ctx.channel, 'Please only respond in DMs')
            return

        if not response:
            await ctx.bot.send_message(ctx.channel,
                'Usage: `{0}respond <TWOW id> <response>`\nUse `{0}id` in the channel to get the id.'.format(ctx.prefix))
            return

        success, response = twow_helper.respond(ctx.bot, identifier, ctx.author.id, response)
        if success == 1:
            await ctx.bot.send_message(ctx.channel,
                'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
        elif success == 3:
            await ctx.bot.send_message(ctx.channel, 'Voting has already started. Sorry.')
        elif success == 5:
            await ctx.bot.send_message(ctx.channel, 'There\'s no prompt.. How can you even? :confounded:')
        elif success == 7:
            await ctx.bot.send_message(ctx.channel, 'You are unable to submit this round. Please wait for the next season.')
        elif success == 9:
            await ctx.bot.send_message(ctx.channel, 'That is a lot of characters. Why don\'t we tone it down a bit?')
        elif success == 11:
            await ctx.bot.send_message(ctx.channel,
                ':no_good: Your response is over {} word{} ({}).'.format(response[0], 's' if response[0] != 1 else '', response[1]))
        else:
            if success // 2 % 2 == 1:
                await ctx.bot.send_message(ctx.channel, ':warning:**Warning! Overwriting current response!**:warning:')
            if success // 8 % 2 == 1:
                await ctx.bot.send_message(ctx.channel, ':unamused: **Due to rude words, your submission has been changed to:**\n{}'.format(response))
            await ctx.bot.send_message(ctx.channel, ':writing_hand: **Submission recorded**')

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def owner(self, ctx, identifier:str = ''):
        '''Get the owner of the mTWOW in the current channel.'''
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}

            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return

            sd = ctx.bot.server_data[s_ids[identifier]]
        else:
            sd = ctx.bot.server_data[ctx.channel.id]

        user = ctx.bot.get_user(sd['owner'])
        print(sd['owner'])
        if sd['canqueue'] and len(sd['queue']) > 0:
            host = ctx.bot.get_user(sd['queue'][0])
            await ctx.bot.send_message(ctx.channel, 'The owner of this mTWOW is {}. {} is hosting.'.format(user.name, host.name))
        else:
            await ctx.bot.send_message(ctx.channel, 'The owner of this mTWOW is {}.'.format(user.name))

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    async def status(self, ctx, identifier:str = ''):
        '''Get information about a mTWOW.'''
        if identifier:
            s_ids = {i[1]:i[0] for i in ctx.bot.servers.items()}

            if identifier not in s_ids:
                await ctx.bot.send_message(ctx.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(identifier.replace('`', '\\`')))
                return

            sd = ctx.bot.server_data[s_ids[identifier]]
            id = s_ids[identifier]
        else:
            sd = ctx.bot.server_data[ctx.channel.id]
            id = ctx.channel.id

        seasonn = sd['season']
        roundn = sd['round']
        round = sd['seasons']['season-{}'.format(seasonn)]['rounds']['round-{}'.format(roundn)]
        round1 = sd['seasons']['season-{}'.format(seasonn)]['rounds']['round-1']
        starta = round1['alive']
        nowa = round['alive']
        alias = ctx.bot.servers[id]
        waiting_for = 'a prompt'
        if round['prompt'] != None and not sd['voting']:
            waiting_for = 'responses'
        elif round['prompt'] != None and sd['voting']:
            waiting_for = 'votes'

        pstatus = 'spectating'
        if sd['canqueue'] and len(sd['queue']) > 0 and sd['queue'][0] == ctx.author.id:
            pstatus = 'hosting'
        elif ctx.author.id in nowa:
            pstatus = 'alive'
        elif ctx.author.id in starta:
            pstatus = 'dead'
        if len(starta) == 1:
            sustr = '1 person'
        else:
            sustr = '{} people'.format(len(starta))
        if len(nowa) == 1:
            alstr = '1 person is'
        else:
            alstr = '{} people are'.format(len(nowa))

        mess = '**Info for {}**\n'.format(alias)
        mess += '{} is on season {} round {}.\n'.format(alias, seasonn, roundn)
        mess += '{} signed up. {} still alive.\n'.format(sustr, alstr)
        mess += 'This TWOW is waiting for {}.\n'.format(waiting_for)

        if waiting_for == 'votes':
            if len(round['votes']) == 1:
                mess += 'There is currently 1 vote and '
            else:
                mess += 'There are currently {} votes and '.format(len(round['votes']))
            if len(round['responses']) == 1:
                mess += '1 response.\n'.format(len(round['responses']))
            else:
                mess += '{} responses.\n'.format(len(round['responses']))

            if round['restimer'] == 'waiting':
                mess += 'Results will start once we get a vote.\n'
            elif type(round['restimer']) == datetime.datetime:
                mess += 'Results will start in {}.\n'.format(delta_to_string(round['restimer']-datetime.datetime.utcnow()))


        elif waiting_for == 'responses':
            if len(round['responses']) == 1:
                mess += 'There is currently 1 response.\n'
            else:
                mess += 'There are currently {} responses.\n'.format(len(round['responses']))

            if round['votetimer'] == 'waiting':
                mess += 'Voting will start once we get 2 responses.\n'
            elif type(round['votetimer']) == datetime.datetime:
                mess += 'Voting will start in {}.\n'.format(delta_to_string(round['votetimer']-datetime.datetime.utcnow()))

        elif waiting_for == 'a prompt':
            if type(sd['hosttimer']) == datetime.datetime:
                mess += 'The host has {} to create a prompt.\n'.format(delta_to_string(sd['hosttimer']-datetime.datetime.utcnow()))

        mess += 'You are {}.\n'.format(pstatus)

        try:
            mess += 'Last season\'s winner was {}. '.format(
                ctx.bot.get_user(sd['seasons']['season-{}'.format(seasonn-1)]['winner']).name)
        except KeyError:
            pass

        try:
            mess += 'Last round\'s winner was {}.'.format(
                ctx.bot.get_user(sd['seasons']['season-{}'.format(seasonn)]['rounds']['round-{}'.format(roundn-1)]['winner']).name)
        except KeyError:
            pass

        await ctx.bot.send_message(ctx.channel, mess)

    @category('twow')
    @commands.command()
    @checks.twow_exists()
    @checks.can_queue()
    async def queue(self, ctx):
        lineup = ctx.bot.server_data[ctx.channel.id]['queue']
        if len(lineup) == 0:
            await ctx.bot.send_message(ctx.channel, 'No one is in the queue!')
        else:
            mess = '**Hosting Queue:**\n'
            changed = False
            for i in list(lineup):
                if ctx.bot.get_user(uid) is None:
                    lineup.remove(i)
                    changed = True
            if changed:
                ctx.bot.save_data()

            mess += '1.) **{}**\n'.format(ctx.bot.get_user(lineup[0]).name)
            for n, uid in enumerate(lineup[1:]):
                mess += '{}.) {}\n'.format(n+2, ctx.bot.get_user(uid).name)
            await ctx.bot.send_message(ctx.channel, mess)

def setup(bot):
    bot.add_cog(TWOW())
