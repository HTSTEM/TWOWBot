# https://discordapp.com/oauth2/authorize?client_id=338683671664001024&scope=bot
#fe80::3455:3ccf:e675:8286
'''
Data format:

responses:
 Username: resonse
 Username: 
 Username: response
slides:
 SlideName:
  A: Username
  B: Userber
  C: Userber
  D: Userber
  E: Userber
  F: Userber
  G: Userber
  H: Userber
  I: Userber
  J: Userber
'''


import datetime
import inspect
import random
import string
import math
import re
import os

from ruamel.yaml import YAML
import discord


TOKEN = open('bot-token.txt').read()
DEVELOPERS = [161508165672763392, 312615171191341056]
VOTE_COLLECTOR = 161508165672763392

VOTE_REGEX = '\[(.*?) ([A-{}]*?)\]'

DEAD_ID = 329368398356283403
ALIVE_ID = 329369355936858112
NTS_ID = 329369440426786818
DNP_ID = 332647826687524867


BOT_HOSTER = 'Bottersnike#3605'


ROUND = 1

SLIDE_NAMES = list(map(str.upper, dir(__builtins__)))

VOTE_URL = 'https://bottersnike.github.io/tlow.html'


class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
    
        if not os.path.exists('round{}.yml'.format(ROUND)):
            open('round{}.yml'.format(ROUND), 'w').close()
        self.yaml = YAML(typ='safe')
        
        with open('round{}.yml'.format(ROUND)) as data_file:
            self.data = self.yaml.load(data_file)
            
        with open('server_data/servers.yml') as data_file:
            self.servers = self.yaml.load(data_file)
            
        self.server_data = {}
        for i in self.servers.keys():
            if '{}.yml'.format(i) in os.listdir('server_data'):
                with open('server_data/{}.yml'.format(i)) as data_file:
                    self.server_data[i] = self.yaml.load(data_file)
        
        if self.data['responses'] is None:
            self.data['responses'] = {}
        if self.data['slides'] is None:
            self.data['slides'] = {}
        if self.data['votes'] is None:
            self.data['votes'] = {}
    
        @self.event
        async def on_ready():
            print('Wubba Lubba Dub Dub!')

        async def send_message(to, msg):
            if len(msg) > 1500:
                await to.send('I might be the cleverest guy in the universe, but I can\'t handle messages over 1500 characters yet.\nThe message started with: ```\n{}```'.format(msg[:1000].replace('`', '`\u200b')))
            else:
                if not random.randint(0, 4):
                    await to.send(msg + ' *Burp*')
                else:
                    await to.send(msg)

        def save_data():
            with open('round{}.yml'.format(ROUND), 'w') as data_file:
                self.yaml.dump(self.data, data_file)
            with open('server_data/servers.yml', 'w') as data_file:
                self.yaml.dump(self.servers, data_file)
            for i in self.server_data.items():
                with open('server_data/{}.yml'.format(i[0]), 'w') as data_file:
                    self.yaml.dump(i[1], data_file)
            
            
            
            if self.data['responses'] is None:
                self.data['responses'] = {}
            if self.data['slides'] is None:
                self.data['slides'] = {}
            if self.data['votes'] is None:
                self.data['votes'] = {}
                 
        @self.event
        async def on_message(message):
            if message.content.startswith('.'):
                raw_command = message.content[1:]
                command = raw_command.split(' ')[0]
                
                raw_args = raw_command[len(command) + 1:].strip()
                args = raw_args.split(' ')
                
                if message.author.id in DEVELOPERS:  # Dev only commands
                    if command == 'say':
                        await send_message(message.channel, raw_args)
                    elif command == 'die':
                        await send_message(message.channel, ':wave:')
                        await self.logout()
                    elif command == 'invite':
                        await send_message(message.channel, '<https://discordapp.com/oauth2/authorize?client_id=338683671664001024&scope=bot>')
                    elif command == 'role_ids':
                        await message.author.send('\n'.join(['{}: {}'.format(role.name.replace('@', '@\u200b'), role.id) for role in message.guild.roles]))
                        await message.channel.send(':mailbox_with_mail:')
                    
                    # Only works on TLOW
                    elif command == 'set_response':
                        uid = args[0]
                        resp = ' '.join(args[1:])
                        self.data['responses'][uid] = resp
                        save_data()
                        await message.channel.send('Wubba Lubba Dub Dub!')
                    elif command == 'gen_slides':
                        slides_no = 3
                        per_slide = math.ceil(len(self.data['responses']) / slides_no * 2)
                        
                        chunks = [[] for i in range(slides_no)]
                        
                        print(per_slide, chunks)
                        
                        pos = 0
                        while not all([len(i) >= per_slide for i in chunks]):
                            for i in self.data['responses'].items():
                                if len(chunks[pos]) >= per_slide:
                                    pos += 1
                                if pos >= slides_no:
                                    pos = 0
                                chunks[pos].append(i)
                                
                                if all([len(i) >= per_slide for i in chunks]):
                                    break

                        for chunk in chunks:
                            random.shuffle(chunk)
                        
                        slides = {}
                        for chunk in chunks:
                            name = None
                            while name is None or name in slides:
                                name = random.choice(SLIDE_NAMES)
                            slides[name] = {}
                            for n, i in enumerate(chunk):
                                slides[name][string.ascii_uppercase[n]] = i[0]
                        
                        self.data['slides'] = slides
                        save_data()
                        
                        await send_message(message.channel, 'Wubba Lubba Dub Dub!')
                    elif command == 'eval':  # TWOW-Bot ready!
                        result = None
                        env = {
                            'guild': message.guild,
                            'author': message.author,
                            'self': self,
                            'message': message,
                            'channel': message.channel
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
                    elif command == 'list_responses':
                        msg = ''
                        for uid, response in self.data['responses'].items():
                            user = self.get_user(int(uid))
                            if user is None:
                                await send_message(message.channel, 'User with ID {} not found.'.format(uid))
                                continue
                            
                            msg += '**{}**:\n{}**{}**\n'.format(user.name, response, '-'*100)
                            
                            if len(msg) > 1000:
                                await message.channel.send(msg)
                                msg = ''

                        if msg:
                            await message.channel.send(msg)
                        
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
                    
                    d = '```ini\n[ ====  RickBot help  ==== ]\n'
                    
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
                        
                    d += '\n[ Made by Bottersnike#3605 ]```'
                    await send_message(message.channel, d)
                
                # Only works on TLOW
                elif command == 'slides' and message.author.id in DEVELOPERS:
                    if len(self.data['slides']) == 0:
                        await send_message(message.channel, 'There aren\'t any voting slides yet.. I\'d try again later.')
                        return
                    
                    if not raw_args:
                        m = '**Avalible slides this round:**\n'
                        m += '\n'.join(['**`{}`**'.format(i) for i in self.data['slides'].keys()])
                        m += '\n*Use `.slides <slide name>` to view a slide.*'
                        
                        await send_message(message.channel, m)
                    else:
                        if raw_args not in self.data['slides']:
                            await send_message(message.channel, 'No slide named `{}` found. Sorry about that.'.format(raw_args.replace('@', '@\u200b')))
                            return
                        
                        msg = '**Submissions in slide `{}`:**\n\n'.format(raw_args)
                        
                        for i in self.data['slides'][raw_args].items():
                            msg += ':regional_indicator_{}:\n```{}```**{}**\n'.format(i[0].lower(), self.data['responses'][i[1]][3:-3].replace('`', '`\u200b'), '-'*100)
                            
                            if len(msg) > 1000:
                                await message.channel.send(msg)
                                msg = ''

                        if msg:
                            await message.channel.send(msg)
                elif command == 'ping':
                    await send_message(message.channel, 'Pong')
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
                elif command == 'usercount':
                    await send_message(message.channel, 'There are currenty {} memebers.'.format(message.guild.member_count))
                elif command == 'contestants':
                    if message.guild.large:
                        await self.request_offline_members(message.guild)
                    
                    dead_r = None
                    alive_r = None
                    contestants = 0
                    
                    for member in message.guild.members:
                        if dead_r is None:
                            for role in member.roles:
                                if role.id == DEAD_ID:
                                    dead_r = role
                        if alive_r is None:
                            for role in member.roles:
                                if role.id == ALIVE_ID:
                                    alive_r = role
                        
                        if alive_r is not None and alive_r in member.roles:
                            contestants += 1
                        elif dead_r is not None and dead_r in member.roles:
                            contestants += 1
                    
                    await send_message(message.channel, 'There are {} contestants so far this season.'.format(contestants))
                elif command == 'alive':
                    if message.guild.large:
                        await self.request_offline_members(message.guild)
                    
                    dead_r = None
                    alive_r = None
                    alive = 0
                    dead = 0
                    
                    for member in message.guild.members:
                        if dead_r is None:
                            for role in member.roles:
                                if role.id == DEAD_ID:
                                    dead_r = role
                        if alive_r is None:
                            for role in member.roles:
                                if role.id == ALIVE_ID:
                                    alive_r = role
                        
                        if alive_r is not None and alive_r in member.roles:
                            alive += 1
                        elif dead_r is not None and dead_r in member.roles:
                            dead += 1
                    
                    await send_message(message.channel, '{} out of {} contestants are alive.'.format(alive, alive + dead))
                elif command == 'dead':
                    if message.guild.large:
                        await self.request_offline_members(message.guild)
                    
                    dead_r = None
                    alive_r = None
                    alive = 0
                    dead = 0
                    
                    for member in message.guild.members:
                        if dead_r is None:
                            for role in member.roles:
                                if role.id == DEAD_ID:
                                    dead_r = role
                        if alive_r is None:
                            for role in member.roles:
                                if role.id == ALIVE_ID:
                                    alive_r = role
                        
                        if alive_r is not None and alive_r in member.roles:
                            alive += 1
                        elif dead_r is not None and dead_r in member.roles:
                            dead += 1
                    
                    await send_message(message.channel, '{} out of {} contestants are dead.'.format(dead, alive + dead))
                elif command == 'responses':
                    await send_message(message.channel, 'I\'ve got {} responses recorded so far.'.format(len(self.data['responses'])))
                elif command in ['nts', 'needstosubmit']:
                    if message.guild.large:
                        await self.request_offline_members(message.guild)
                    
                    dead_r = None
                    alive_r = None
                    nts_r = None
                    alive = 0
                    dead = 0
                    nts = 0
                    
                    for member in message.guild.members:
                        if dead_r is None:
                            for role in member.roles:
                                if role.id == DEAD_ID:
                                    dead_r = role
                        if alive_r is None:
                            for role in member.roles:
                                if role.id == ALIVE_ID:
                                    alive_r = role
                        if nts_r is None:
                            for role in member.roles:
                                if role.id == NTS_ID:
                                    nts_r = role
                        
                        if alive_r is not None and alive_r in member.roles:
                            alive += 1
                        elif dead_r is not None and dead_r in member.roles:
                            dead += 1
                        if nts_r is not None and nts_r in member.roles:
                            nts += 1
                    
                    await send_message(message.channel, '{} out of {} contestants still need to submit.'.format(nts, alive + dead))
                elif command == 'vote_leg':  # Legacy. Replacement in place.
                    if not raw_args:
                        await send_message(message.channel, 'Provided voting is open, you can see the slides at {}.\nTo vote, do `.vote <your vote>` either here or in a DM with me.'.format(VOTE_URL))
                    else:
                        if len(self.data['slides']) == 0:
                            await send_message(message.channel, 'There aren\'t any voting slides yet.. I\'d try again later.')
                            return
                    
                        per_slide = len(self.data['slides'][list(self.data['slides'].keys())[0]])
                    
                        raw_args = raw_args.upper()
                        found = re.findall(VOTE_REGEX.format(string.ascii_uppercase[per_slide - 1]), raw_args)
                                
                        if len(found) < 1:
                            if not isinstance(message.channel, discord.abc.PrivateChannel):
                                await send_message(message.author, 'Your vote doesn\'t seem to be in the right form.\nIt should follow the form `[<SLIDE NAME> <YOUR VOTE>]`.\nFor example: `[LAMBDA ABCDEFGHIJ]`')
                                await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                await message.delete()
                                
                                await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                            else:
                                await send_message(message.channel, 'Your vote doesn\'t seem to be in the right form.\nIt should follow the form `[<SLIDE NAME> <YOUR VOTE>]`.\nFor example: `[LAMBDA ABCDEFGHIJ]`')
                            return
                            
                        for f in found:
                            slide, vote = f
                            
                            seen = []
                            for i in vote:
                                if i not in seen:
                                    seen.append(i)
                                else:                        
                                    if not isinstance(message.channel, discord.abc.PrivateChannel):
                                        await send_message(message.author, 'Please don\'t repeat any submissions in the same vote.')
                                        await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                        await message.delete()
                                        
                                        await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                                    else:
                                        await send_message(message.channel, 'Please don\'t repeat any submissions in the same vote.')
                                    continue
                                
                            if len(vote) != per_slide:
                                if not isinstance(message.channel, discord.abc.PrivateChannel):
                                    await send_message(message.author, 'Please vote on all {} submissions on the slide exactly once.'.format(per_slide))
                                    await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                    await message.delete()
                                    
                                    await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                                else:
                                    await send_message(message.channel, 'Please vote on all {} submissions on the slide exactly once.'.format(per_slide))
                                continue
                            
                            # TODO: Move all voting over to the bot and the here there would be checks
                            #       to see if the user has already voted on that slide.
                            if slide not in self.data['slides']:
                                if not isinstance(message.channel, discord.abc.PrivateChannel):
                                    await send_message(message.author, 'No slide found called `{}` was found.'.format(slide.replace('@', '@\u200b')))
                                    await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                    await message.delete()
                                    
                                    await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                                else:
                                    await send_message(message.channel, 'No slide found called `{}` was found.'.format(slide.replace('@', '@\u200b')))
                                continue
                            
                            vote_id = '{}-{}'.format(message.author.id, slide)
                            if vote_id in self.data['votes']:
                                if not isinstance(message.channel, discord.abc.PrivateChannel):
                                    await send_message(message.author, 'You have already voted on this slide.')
                                    await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                    await message.delete()
                                    
                                    await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                                else:
                                    await send_message(message.channel, 'You have already voted on this slide.')
                                continue
                            
                            self.data['votes'][vote_id] = vote
                            save_data()
                            
                            collector = self.get_user(VOTE_COLLECTOR)
                            await collector.send('{} has voted on slide `{}` with `{}`!'.format(message.author.name, slide, vote))
                            
                            if not isinstance(message.channel, discord.abc.PrivateChannel):
                                await send_message(message.author, 'Your vote has been recorded. Thank you!'.format(collector.name))
                                await send_message(message.author, 'Your vote was `{}` for reference.'.format(raw_args))
                                await message.delete()
                                
                                await send_message(message.channel, ':mailbox_with_mail: {}'.format(message.author.mention))
                            else:
                                await send_message(message.channel, 'Your vote has been recorded. Thank you!'.format(collector.name))
                
                # TWOW-Bot ready!
                elif command == 'id':
                    if message.guild.id in self.servers:
                        await send_message(message.channel, 'This server\'s identifier is `{}`'.format(self.servers[message.guild.id]))
                    else:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data. If this is an error, please contact {}.'.format(BOT_HOSTER))
                elif command == 'prompt':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.guild.id]
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': {}}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        await send_message(message.channel, 'There\'s no prompt set yet for this mTWOW.')
                        return
                    
                    await send_message(message.channel, 'The current prompt is:\n{}\n'.format(round['prompt']))
                elif command == 'season':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.guild.id]
                    
                    await send_message(message.channel, 'We are on season {}'.format(sd['season']))
                elif command == 'round':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.guild.id]
                    
                    await send_message(message.channel, 'We are on round {}'.format(sd['round']))
                elif command == 'vote':
                    pass  # TODO
                elif command == 'respond':
                    if not isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.delete()
                        await send_message(message.channel, 'Please only respond in DMs')
                        return
                    
                    if len(args) < 2:
                        await send_message(message.channel, 'Usage: `.respond <TWOW id> <response>\nUse `.id` in the server to get the id.')
                        return
                    
                    id, response = raw_args.split(' ', 1)
                    s_ids = {i[1]:i[0] for i in self.servers.items()}
                    
                    if id not in s_ids:
                        await send_message(message.chanel, 'I can\'t find any mTWOW under the name `{}`.'.format(id.replace('`', '\\`')))
                        return
                    
                    sd = self.server_data[s_ids[id]]
                    
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': {}}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        await send_message(message.channel, 'There\'s no prompt.. How can you even?')
                        return
                    
                    if message.author.id in round['responses']:
                        await send_message(message.channel, '**Warning! Overwriting current response!**')
                    if len(response.split(' ')) > 10:
                        await send_message(message.channel, '**Warning! Your response looks to be over 10 words ({}).**\nThis can be ignored if you are playing a variation TWOW that doesn\'t have this limit'.format(len(response.split(' '))))
                    
                    round['responses'][message.author.id] = response
                    await send_message(message.channel, '**Submission recorded**')
                    
                    save_data()
                        
                # TWOW owner only commands
                elif command == 'register':
                    if message.guild.id in self.servers:
                        owner = self.get_user(self.server_data[message.guild.id]['owner'])
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
                                               'votes': {},
                                              }
                                             }
                                            }
                            }
                            
                            self.server_data[message.guild.id] = s
                            self.servers[message.guild.id] = raw_args
                            
                            save_data()
                        
                            await send_message(message.channel, 'Woah! I just set up a whole mTWOW for you under the name `{}`!\nPlease now use `.setup` to configure your mTWOW before it can be used.'.format(raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        else:
                            await send_message(message.channel, 'Usage: `.register <short identifier>')
                elif command == 'setup':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                        
                    if self.server_data[message.guild.id]['owner'] != message.author.id:
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
                    
                    self.server_data[message.guild.id]['ids'][key] = value
                    save_data()
                    
                    await send_message(message.channel, 'Wubba lubba dub dub! (Done)')
                elif command == 'show_config':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                        
                    if self.server_data[message.guild.id]['owner'] != message.author.id:
                        return
                    
                    await send_message(message.channel, str(self.server_data[message.guild.id]))
                elif command == 'set_prompt':
                    if message.guild.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this server in my data.')
                        return
                    
                    sd = self.server_data[message.guild.id]
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    # If you're someone who likes all code to look pristine, I appologise for the next few lines :'(
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {}
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': {}}
                    
                    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
                    
                    if round['prompt'] is None:
                        round['prompt'] = raw_args.replace('@', '@\u200b').replace('`', '\\`')
                        save_data()
                        await send_message(message.channel, 'The prompt has been set to `{}` for this round.'.format(raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        return
                    else:
                        await send_message(message.channel, 'The prompt has been changed from `{}` to `{}` for this round.'.format(round['prompt'], raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        round['prompt'] = raw_args.replace('@', '@\u200b').replace('`', '\\`')
                        save_data()
                        return
    
    def start_bot(self):
        self.run(TOKEN)


# .replace('@', '@\u200b')
        
if __name__ == '__main__':
    b = Bot()
    b.start_bot()