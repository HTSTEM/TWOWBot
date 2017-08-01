# https://discordapp.com/oauth2/authorize?client_id=338683671664001024&scope=bot

''' TODO:

[x] Voting [DONE]
[X] Results [DONE]
[X] Limit responding to alives [DONE]
[ ] Handle DNPs
[ ] Round/Season incrementation
[ ] Make things like voting only work once everyone's responded


'''

import builtins
import datetime
import asyncio
import inspect
import random
import string
import math
import re
import os

from ruamel.yaml import YAML
import discord


TOKEN = open('bot-token.txt').read().split('\n')[0] #stupid file endings
DEVELOPERS = [161508165672763392, 312615171191341056, 240995021208289280]

RESPONSES_PER_SLIDE = 8

SUPERSCRIPT = ['ˢᵗ', 'ᶮᵈ', 'ʳᵈ', 'ᵗʰ']

ELIMINATION = 0.6  # Fraction of results that are safe

# This is used in error messages where the hoster might need to manually
# change some of the .yml files
BOT_HOSTER = 'Bottersnike#3605'

class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        '''
        if not os.path.exists('round{}.yml'.format(ROUND)):
            open('round{}.yml'.format(ROUND), 'w').close()'''
        self.yaml = YAML(typ='safe')
            
        with open('server_data/servers.yml') as data_file:
            self.servers = self.yaml.load(data_file)
            
        self.server_data = {}
        for i in self.servers.keys():
            if '{}.yml'.format(i) in os.listdir('server_data'):
                with open('server_data/{}.yml'.format(i)) as data_file:
                    self.server_data[i] = self.yaml.load(data_file)
    
        @self.event
        async def on_ready():
            print('Logged in as {}#{}'.format(self.user.name,self.user.discriminator))
            print(self.user.id)

        async def send_message(to, msg):
            if len(msg) > 1500:
                await to.send('I might be the cleverest guy in the universe, but I can\'t handle messages over 1500 characters yet.\nThe message started with: ```\n{}```'.format(msg[:1000].replace('`', '`\u200b')))
            else:
                if not random.randint(0, 4):
                    await to.send(msg + ' *Burp*')
                else:
                    await to.send(msg)

        def save_data():
            with open('server_data/servers.yml', 'w') as data_file:
                self.yaml.dump(self.servers, data_file)
            for i in self.server_data.items():
                with open('server_data/{}.yml'.format(i[0]), 'w') as data_file:
                    self.yaml.dump(i[1], data_file)
               
        @self.event
        async def on_message(message):
            if message.content.startswith('.'):
                raw_command = message.content[1:]
                command = raw_command.split(' ')[0].lower()
                
                raw_args = raw_command[len(command) + 1:].strip()
                args = raw_args.split(' ')
                
                if message.author.id in DEVELOPERS:  # Dev only commands
                    if command == 'say':  # Say somethin'
                        await send_message(message.channel, raw_args)
                    elif command == 'die':  # Logout
                        await send_message(message.channel, ':wave:')
                        await self.logout()
                    elif command == 'invite':  # Get the RickBot invite url
                        await send_message(message.channel, '<https://discordapp.com/oauth2/authorize?client_id=338683671664001024&scope=bot>')
                    elif command == 'role_ids':  # DM a list of the IDs of all the roles
                        await message.author.send('\n'.join(['{}: {}'.format(role.name.replace('@', '@\u200b'), role.id) for role in message.channel.roles]))
                        await message.channel.send(':mailbox_with_mail:')
                    elif command == 'eval':  # NEEDS TO BE MADE OWNER ONLY!
                        result = None
                        env = {
                            'channel': message.channel,
                            'author': message.author,
                            'self': self,
                            'message': message,
                            'channel': message.channel,
                            'save_data': save_data,
                        }
                        env.update(globals())

                        try:
                            result = eval(raw_args, env)

                            if inspect.isawaitable(result):
                                result = await result

                            colour = 0x00FF00
                        except Exception as e:
                            result = type(e).__name__ + ': ' + str(e)
                            colour = 0xFF0000

                        embed = discord.Embed(colour=colour, title=raw_args, description='```py\n{}```'.format(result))
                        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                        await message.channel.send(embed=embed)
                
                # General util                
                if command == 'help':
                    commands = {
                        'help': 'This message',
                        'ping': 'Ping the bot',
                        'me': 'Get info about yourself (also aboutme)',
                        'usercount': 'Get the server user count',
                        'contestants': 'Get the number of contestants',
                        'alive': 'Get the number of alive contestants',
                        'dead': 'Get the number of dead contestants',
                        'nts': 'Get the number of people who need to submit still (also needtosubmit)',
                        'responses': 'Get the number of responses stored in the bot',
                        'slides': 'View the slides for voting',
                        'vote': 'Vote!!',
                    }
                    n = len(max(list(commands.keys()), key=lambda x:len(x)))
                    
                    d = '```ini\n[ ====  TwowBot help  ==== ]\n'
                    
                    if not raw_args:
                        d += '\n'.join(['{}{}={}'.format(i[0], ' ' * (n - len(i[0]) + 1), i[1]) for i in commands.items()])
                    else:
                        while '  ' in raw_args:
                            raw_args = raw_args.replace('  ', ' ')
                        raw_args = raw_args.strip()
                        raw_args = raw_args.replace('[', '')
                        raw_args = raw_args.replace(']', '')
                        raw_args = raw_args.replace('\n', ' ')
                        raw_args = raw_args.replace('=', '')
                        
                        passed = list(set(raw_args.split(' ')))
                    
                        n = len(max(passed, key=lambda x:len(x)))
                    
                        for i in passed:
                            if i in commands:
                                d += '{}{}={}\n'.format(i, ' ' * (n - len(i) + 1), commands[i])
                            else:
                                d += '{}{}=Command not found\n'.format(i.replace('@', '@\u200b').replace('`', '`\u200b'), ' ' * (n - len(i) + 1))
                        d = d[:-1]
                        
                    d += '\n[ Made by Bottersnike#3605, hanss314#0128 and Noahkiq#0493 ]```'
                    await send_message(message.channel, d)
                elif command in ['me', 'boutme', '\'boutme', 'aboutme']:
                    member = message.author
                    
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

                    embed.add_field(name='Roles', value='\n'.join([r.mention for r in sorted(member.roles, key=lambda x:x.position, reverse=True) if r.name != '@everyone']))

                    embed.set_author(name=member, icon_url=avatar)

                    await message.channel.send(embed=embed)
                elif command == 'ping':
                    await send_message(message.channel, 'Pong')
                
                # TWOW-Bot ready!
                elif command == 'id':  # Gets the server ID used in voting
                    if message.channel.id in self.servers:
                        await send_message(message.channel, 'This server\'s identifier is `{}`'.format(self.servers[message.channel.id]))
                    else:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data. If this is an error, please contact {}.'.format(BOT_HOSTER))
                elif command == 'prompt':  # Gets the current prompt
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        await send_message(message.channel, 'There\'s no prompt set yet for this mTWOW.')
                        return
                    
                    await send_message(message.channel, 'The current prompt is:\n{}\n'.format(round['prompt'].decode('utf-8')))
                elif command == 'season':  # Gets the current season number
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    await send_message(message.channel, 'We are on season {}'.format(sd['season']))
                elif command == 'round':  # Get the current round number
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    await send_message(message.channel, 'We are on round {}'.format(sd['round']))
                elif command == 'vote':  # I think it makes me a hot dog. Not sure.
                    if not isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.delete()
                        await send_message(message.channel, 'Please only vote in DMs')
                        return
                    
                    if len(args) > 2 or not args[0]:
                        await send_message(message.channel, 'Usage: `.vote <TWOW id> [vote]\nUse `.id` in the server to get the id.')
                        return
                    print(args)
                    
                    id = args[0]
                    
                    s_ids = {i[1]:i[0] for i in self.servers.items()}
                    
                    if id not in s_ids:
                        await send_message(message.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(id.replace('`', '\\`')))
                        return
                    
                    sd = self.server_data[s_ids[id]]
                    
                    if not sd['voting']:
                        await send_message(message.channel, 'Voting hasn\'t started yet. Sorry.')
                        return
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if len(args) == 1:  # New slides needed!
                        if message.author.id not in round['slides']:
                            # Sort all responses based off their number of votes
                            responses = [[i, 0] for i in round['responses']]
                            for i in responses:
                                if i[0] == message.author.id:
                                    responses.remove(i)
                            for vote in round['votes']:
                                # Each vote is a list of user IDs going from best to worst
                                for i in vote['vote']:
                                    for r in responses:
                                        if r[0] == i:
                                            r[1] += 1
                                            break
                                    else:
                                        if i != message.author.id:
                                            responses.append([i, 1])
                            responses.sort(key=lambda x:x[1])

                            if len(responses) == 0:
                                await send_message(message.author, 'I don\'t have enough responses to formulate a slide. Sorry.')
                                return
                            
                            # ~~Calculate the nubmer of responses per slide~~ Global at start of file.
                            # Take that many items from the list of responses.
                            
                            slide = responses[:RESPONSES_PER_SLIDE]
                            slide = [i[0] for i in slide]
                            random.shuffle(slide)
                            
                            # Save as a slide.
                            
                            round['slides'][message.author.id] = slide
                            
                            save_data()
                        
                        slide = round['slides'][message.author.id]
                        
                        m = '**Your slide is:**'
                        for n, i in enumerate(slide):
                            m += '\n:regional_indicator_{}: {}'.format(string.ascii_lowercase[n], round['responses'][i])
                            if len(m) > 1500:
                                await message.channel.send(m)
                                m = ''
                        if m:
                            await message.channel.send(m)
                    else:
                        id, vote_str = raw_args.upper().split(' ')
                        if message.author.id not in round['slides']:
                            await send_message(message.author, 'You don\'t have a voting slide *to* vote on!\nUse `.vote {}` to generate one.'.format(id))
                            return
                            
                        slide = round['slides'][message.author.id]
                        to = string.ascii_uppercase[len(slide) - 1]
                        regex = '[A-{}]{{{}}}'.format(to, len(slide))
                        if not re.compile(regex).match(vote_str):
                            await send_message(message.author, 'Please vote for **every** item on your slide exactly **once**.')
                            return
                        
                        if len(set(vote_str)) != len(vote_str):  # Check for repeats
                            await send_message(message.author, 'Please vote for **every** item on your slide exactly **once**.')
                            return
                        
                        vote = list(vote_str)
                        for n, i in enumerate(vote):
                            vote[n] = slide[string.ascii_uppercase.index(i)]
                        
                        round['votes'].append({
                            'voter': message.author.id,
                            'vote': vote
                        })
                        
                        del round['slides'][message.author.id]
                        save_data()
                        
                        await send_message(message.channel, 'Thanks for voting!')
                elif command == 'respond':  # Probbly handles the controlling of my kitten army
                    if not isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.delete()
                        await send_message(message.channel, 'Please only respond in DMs')
                        return
                    
                    if len(args) < 2:
                        await send_message(message.channel, 'Usage: `.respond <TWOW id> <response>`\nUse `.id` in the server to get the id.')
                        return
                    
                    id, response = raw_args.split(' ', 1)
                    s_ids = {i[1]:i[0] for i in self.servers.items()}
                    
                    if id not in s_ids:
                        await send_message(message.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(id.replace('`', '\\`')))
                        return
                    
                    sd = self.server_data[s_ids[id]]
                    
                    if sd['voting']:
                        await send_message(message.channel, 'Voting has already started. Sorry.')
                        return
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        await send_message(message.channel, 'There\'s no prompt.. How can you even?')
                        return
                    
                    for role in self.get_channel(s_ids[id]).roles:
                        if role.id == sd['ids']['alive']:
                            alive_role = role
                            break
                    else:
                        alive_role = None
                    member = self.get_channel(s_ids[id]).get_member(int(message.author.id))
                    if sd['round'] > 1 and alive_role not in member.roles:
                        await send_message(message.channel, 'You are unable to submit this round. Please wait for the next season.')
                        return
                    
                    if message.author.id in round['responses']:
                        await send_message(message.channel, '**Warning! Overwriting current response!**')
                    if len(response.split(' ')) > 10:
                        await send_message(message.channel, '**Warning! Your response looks to be over 10 words ({}).**\nThis can be ignored if you are playing a variation TWOW that doesn\'t have this limit'.format(len(response.split(' '))))
                    
                    changed = False
                    with open('banned_words.txt') as bw:
                        banned_w = bw.read().split('\n')
                    for i in banned_w:
                        if i:
                            if i in response:
                                response = response.replace(i, '\\*' * len(i))
                                changed = True
                    if changed:
                        await send_message(message.channel, '**Due to rude words, your submission has been changed to:**\n{}'.format(response))
                    
                    round['responses'][message.author.id] = response.encode('utf-8')
                    await send_message(message.channel, '**Submission recorded**')
                    
                    save_data()
                        
                # TWOW owner only commands
                elif command == 'start_voting':
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    if sd['voting']:
                        await send_message(message.channel, 'Voting is already active.')
                        return
                    
                    sd['voting'] = True
                    save_data()
                    await send_message(message.channel, 'Voting has been activated.')
                    return
                elif command == 'results':  # Woah? Results. Let's hope I know how to calculate these.. Haha. I didn't.
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    if not sd['voting']:
                        await send_message(message.channel, 'Voting hasn\'t even started yet...')
                        return
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    
                    totals = {}
                    for r in round['responses']:
                        totals[r] = {'borda': 0, 'votes': 0, 'raw_borda': []}
                    
                    vote_weights = {}
                    
                    for vote in round['votes']:
                        if vote['voter'] not in vote_weights:
                            vote_weights['voter'] = 1
                        else:
                            vote_weights['voter'] += 1
                    for i in vote_weights:
                        vote_weights[i] = 1 / vote_weights[i]
                    
                    for vote in round['votes']:
                        c = len(vote['vote'])
                        for n, v in enumerate(vote['vote']):
                            bc = c - n - 1
                            totals[v]['borda'] += bc
                            totals[v]['votes'] += 1
                            totals[v]['raw_borda'].append(bc / (c - 1) * 100)
                    
                    totals = [{'name': i[0], **i[1]} for i in totals.items()]
                    
                    def f(v):
                        return (v['borda'] / v['votes']) / (len(round['votes'][0]['vote']) - 1) * 100
                    
                    totals.sort(key=f, reverse=True)

                    msg = '**Results for round {}, season {}:**'.format(sd['round'], sd['season'])
                    
                    await message.delete()
                    await message.channel.send(msg)
                    
                    eliminated = []
                    living = []
                    
                    for n, v in list(enumerate(totals))[::-1]:
                        score = f(v)
  
                        mean = sum(v['raw_borda']) / len(v['raw_borda'])
                        variance = sum((i - mean) ** 2 for i in v['raw_borda']) / len(v['raw_borda'])
                        stdev = variance ** 0.5
                    
                        user = message.channel.get_member(v['name'])
                        if user is not None:
                            name = user.mention
                        else:
                            name = str(v['name'])
                    
                        if str(n + 1)[-1] == '1':
                            if n + 1 == 11:
                                symbol = SUPERSCRIPT[3]
                            else:
                                symbol = SUPERSCRIPT[0]
                        elif str(n + 1)[-1] == '2':
                            if n + 1 == 12:
                                symbol = SUPERSCRIPT[3]
                            else:
                                symbol = SUPERSCRIPT[1]
                        elif str(n + 1)[-1] == '3':
                            if n + 1 == 13:
                                symbol = SUPERSCRIPT[3]
                            else:
                                symbol = SUPERSCRIPT[2]
                        else:
                            symbol = SUPERSCRIPT[3]
                    
                        dead = n > ELIMINATION * len(totals)
                        if dead:
                            eliminated.append((name, user, v))
                        else:
                            living.append((name, user, v))
                        
                        msg = '\n{}\n{} **{}{} place**: *{}*\n**{}** ({}% σ={})'.format('=' * 50, ':coffin:' if dead else ':white_check_mark:', n + 1, symbol, round['responses'][v['name']].decode('utf-8'), name, builtins.round(score, 2), builtins.round(stdev, 2))

                        await asyncio.sleep(len(totals) - n / 2)
                        await message.channel.send(msg)
                        
                    user = message.channel.get_member(totals[0]['name'])
                    if user is not None:
                        name = user.mention
                    else:
                        name = str(v['name'])
                    msg = '{}\nThe winner was {}! Well done!'.format('=' * 50, name)
                    await message.channel.send(msg)
                    
                    await message.channel.send('Sadly though, we have to say goodbye to {}.'.format(', '.join([i[0] for i in eliminated])))
                    
                    for role in message.channel.roles:
                        if role.id == sd['ids']['alive']:
                            alive_role = role
                            break
                    else:
                        alive_role = None
                    for role in message.channel.roles:
                        if role.id == sd['ids']['dead']:
                            dead_role = role
                            break
                    else:
                        dead_role = None
                    
                    # Do all the round incrementing and stuff.
                    if len(totals) - len(eliminated) <= 1:
                        await message.channel.send('**This season has ended! The winner was {}!**'.format(name))
                        sd['round'] = 1
                        sd['season'] += 1
                    else:
                        sd['round'] += 1
                        await message.channel.send('**We\'re now on round {}!**'.format(sd['round']))
                        
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    sd['voting'] = False
                    
                    save_data()
                    
                    # Oh yeah, and kill off dead people
                    if alive_role is not None:
                        #for e in eliminated:
                        #    if e[1] is not None:
                        #        if alive_role in e[1].roles:
                        #            await e[1].remove_roles(alive_role, reason='Contestant eliminated')
                        #            if dead_role is not None:
                        #                await e[1].add_roles(dead_role, reason='Contestant eliminated')
                                                
                        
                        if message.channel.large:
                            await self.request_offline_members(message.channel)
                    
                        alive_r = None
                        
                        for member in message.channel.members:
                            if alive_r is None:
                                for role in member.roles:
                                    if role.id == ALIVE_ID:
                                        alive_r = role
                            
                            if alive_r is not None and alive_r in member.roles:
                                for i in living:
                                    if i[1] == member:
                                        break
                                else:
                                    await member.remove_roles(alive_r, reason='Contestant eliminated')
                elif command == 'responses':  # List all responses this round
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                        
                    if self.server_data[message.channel.id]['owner'] != message.author.id:
                        return
                        
                    sd = self.server_data[message.channel.id]
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    m = '**Responses for season {}, round {} so far:**'.format(sd['season'], sd['round'])
                    for i in round['responses'].items():
                        u = self.get_user(i[0])
                        if u is not None:
                            n = u.name
                        else:
                             n = i[0]
                        m += '\n**{}**: {}'.format(n, i[1].decode('utf-8'))
                        if len(m) > 1500:
                            await message.author.send(m)
                            m = ''
                    if m:
                        await message.author.send(m)
                    
                    await send_message(message.channel, ':mailbox_with_mail:')
                elif command == 'register':  # Setup server initially
                    if message.channel.id in self.servers:
                        owner = self.get_user(self.server_data[message.channel.id]['owner'])
                        if owner is not None:
                            await send_message(message.channel, 'This server is already setup. The owner is {}.'.format(owner.name.replace('@', '@\u200b')))
                        else:
                            await send_message(message.channel, 'I can\'t find the owner of this server. Please contact {} to resolve this.'.format(BOT_HOSTER))
                    else:
                        if raw_args:
                            if ' ' in raw_args:
                                await send_message(message.channel, 'No spaces in the identifier please')
                                return
                            if raw_args in list(self.servers.values()):
                                await send_message(message.channel, 'There\'s already a mTWOW setup with that name. Sorry.')
                                return
                            
                            s = {}
                            s['owner'] = message.author.id
                            s['round'] = 1
                            s['season'] = 1
                            s['voting'] = False
                            s['ids'] = {
                                'dead': None,
                                'alive': None,
                                'nts': None
                            }
                            s['seasons'] = {'season-1':
                                            {'rounds':
                                             {'round-1':
                                              {'prompt': None,
                                               'responses': {},
                                               'slides': {},
                                               'votes': [],
                                              }
                                             }
                                            }
                            }
                            
                            self.server_data[message.channel.id] = s
                            self.servers[message.channel.id] = raw_args
                            
                            save_data()
                        
                            await send_message(message.channel, 'Woah! I just set up a whole mTWOW for you under the name `{}`!\nPlease now use `.setup` to configure your mTWOW before it can be used.'.format(raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        else:
                            await send_message(message.channel, 'Usage: `.register <short identifier>')
                elif command == 'setup':  # Set congifs
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                        
                    if self.server_data[message.channel.id]['owner'] != message.author.id:
                        return

                    if len(args) < 2:
                        await send_message(message.channel, 'Usage: `.setup <key> <value>`\nWhere key is one of `dead`, `alive`, `nts` and the value is the ID of the user or role.\nUse `.role_ids` to get the IDs of the roles.')
                        return
                    key, value = raw_args.lower().split(' ', 1)
                    
                    if key not in ['dead', 'alive', 'nts']:
                        await send_message(message.channel, 'The key must be `dead`, `alive` or `nts`.')
                        return
                    
                    try:
                        value = int(value)
                    except ValueError:
                        await send_message(message.channel, 'The value must be an id (as an integer).')
                        return
                    
                    self.server_data[message.channel.id]['ids'][key] = value
                    save_data()
                    
                    await send_message(message.channel, 'Wubba lubba dub dub! (Done)')
                elif command == 'show_config':  # More deguggy really, returns the dict for the server
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                        
                    if self.server_data[message.channel.id]['owner'] != message.author.id:
                        return
                    
                    await send_message(message.channel, str(self.server_data[message.channel.id]))
                elif command == 'set_prompt':  # Summon unicorns
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    # If you're someone who likes all code to look pristine, I appologise for the next few lines :'(
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        round['prompt'] = raw_args.replace('@', '@\u200b').replace('`', '\\`').encode('utf-8')
                        save_data()
                        await send_message(message.channel, 'The prompt has been set to `{}` for this round.'.format(raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        return
                    else:
                        await send_message(message.channel, 'The prompt has been changed from `{}` to `{}` for this round.'.format(round['prompt'].decode('utf-8'), raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        round['prompt'] = raw_args.replace('@', '@\u200b').replace('`', '\\`').encode('utf-8')
                        save_data()
                        return
    
    def start_bot(self):
        self.run(TOKEN)


# .replace('@', '@\u200b')
        
if __name__ == '__main__':
    b = Bot()
    b.start_bot()
