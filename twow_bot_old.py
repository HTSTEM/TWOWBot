''' TODO:

[x] Voting [DONE]
[X] Results [DONE]
[X] Limit responding to alives [DONE]
[X] Handle DNPs
[X] Round/Season incrementation [DONE]
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



TOKEN = ''
DEVELOPERS = []
BOT_HOSTER = ''

yaml = YAML(typ='safe')
with open('config.yml') as data_file:
    cfg = yaml.load(data_file)
    TOKEN = cfg['token']
    DEVELOPERS = cfg['ids']['developers']
    BOT_HOSTER = cfg['ids']['host']

RESPONSES_PER_SLIDE = 8

SUPERSCRIPT = ['ˢᵗ', 'ᶮᵈ', 'ʳᵈ', 'ᵗʰ']

ELIMINATION = 0.6  # Fraction of results that are safe

PREFIX = '.'

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
            try:
                if len(msg) > 2000:
                    await to.send('Whoops! Discord won\'t let me send messages over 2000 characters.\nThe message started with: ```\n{}```'.format(msg[:1000].replace('`', '`\u200b')))
                else:
                    await to.send(msg)
                pass
            except discord.errors.Forbidden:
                pass
        def save_data():
            with open('server_data/servers.yml', 'w') as data_file:
                self.yaml.dump(self.servers, data_file)
            for i in self.server_data.items():
                with open('server_data/{}.yml'.format(i[0]), 'w') as data_file:
                    self.yaml.dump(i[1], data_file)
                    
        def save_archive(sid):
             with open('./server_data/archive/{}-{}.yml'.format(sid,datetime.datetime.utcnow()), 'w') as data_file:
                self.yaml.dump(self.server_data[sid], data_file)
               
        @self.event
        async def on_message(message):
            if message.content.startswith(PREFIX) and not message.content.startswith(PREFIX*2):
                raw_command = message.content[len(PREFIX):]
                command = raw_command.split(' ')[0].lower()
                
                raw_args = raw_command[len(command) + 1:].strip()
                args = raw_args.split(' ')
                
                if message.author.id in DEVELOPERS:  # Dev only commands
                    if command == 'say':  # Say somethin'
                        await send_message(message.channel, raw_args)
                    elif command == 'die':  # Logout
                        await send_message(message.channel, ':wave:')
                        await self.logout()
                    elif command == 'role_ids':  # DM a list of the IDs of all the roles
                        await send_message(message.author,
                            '\n'.join(['{}: {}'.format(role.name.replace('@', '@\u200b'), role.id) for role in message.guild.roles]))
                        await send_message(message.channel,':mailbox_with_mail:')
                    elif command == 'eval' and message.author.id == BOT_HOSTER:
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
                        try:
                            await message.channel.send(embed=embed)
                        except discord.errors.Forbidden:
                            pass
                
                # General util                
                if command == 'help':
                    commands = {
                        'help':('[command]','get help on commands.'),
                        'ping':('','ping the bot.'),
                        'me':('','tells you about yourself.'),
                        'about':('','about TWOWBot.'),
                        'id':('','get the twow id of the current channel.'),
                        'prompt':('','get the prompt of the current channel.'),
                        'season':('','get the season of the current channel.'),
                        'round':('','get the round of the current channel'),
                        'respond':('<mtwow id> <response>','respond to a prompt.'),
                        'vote':('<mtwow id> [vote]','vote on a mTWOW.'),
                        'register':('<mtwow id>','registers the current channel with an id'),
                        'show_config':('[mtwow id]','get the database for a channel.'),
                        'responses':('[mtwow id]','get the responses for this round.'),
                        'set_prompt':('<prompt>','set the prompt for the current channel.'),
                        'start_voting':('','starts voting for the current channel.'),
                        'results':('[elimination]','get the results for the current mTWOW. Specify elimination amount using a number or percentage using `%`. Defaults to 20%.'),
                        'transfer':('<user>','transfer ownership of mtwow to someone else.'),
                        'delete':('','delete the current mtwow.')
                    }
                    n = len(max(list(commands.keys()), key=lambda x:len(x)))
                    
                    d = '**TWOWBot help:**\n'
                    
                    if not raw_args:
                        d += '\n'.join(['`{}{} {}` - {}'.format(PREFIX,i[0], i[1][0], i[1][1]) for i in commands.items()])
                    else:
                        while '  ' in raw_args:
                            raw_args = raw_args.replace('  ', ' ')
                        raw_args = raw_args.strip()
                        raw_args = raw_args.replace('\n', ' ')
                        
                        passed = list(set(raw_args.split(' ')))
                                        
                        for i in passed:
                            if i in commands:
                                d += '`{}{} {}` - {}\n'.format(PREFIX, i, commands[i][0], commands[i][1])
                            else:
                                d += '`{}{}` - Command not found\n'.format(PREFIX, i.replace('@', '@\u200b').replace('`', '`\u200b'))
                        d = d[:-1]
                        
                    d += '\n*Made by Bottersnike#3605, hanss314#0128 and Noahkiq#0493*'
                    await send_message(message.channel, d)
                    
                elif command == 'about':  # Get the RickBot invite url
                    mess = '**This bot was developed by:**\n'
                    mess += 'Bottersnike#3605\n'
                    mess += 'hanss314#0128\n'
                    mess += 'Noahkiq#0493\n'
                    mess += '\n**This bot is being hosted by:**\n'
                    mess += '{}\n'.format(self.get_user(BOT_HOSTER))
                    #mess +='**\nTWOWBot\'s avatar by:**\n'
                    #mess += 'name#discrim\n'
                    mess += '\n**Resources:**\n'
                    mess += '*The official TWOWBot discord server:* https://discord.gg/eZhpeMM\n'
                    mess += '*Go contribute to TWOWBot on GitHub:* https://github.com/HTSTEM/TWOW_Bot\n'
                    mess += '*Invite TWOWBot to your server:* <https://discordapp.com/oauth2/authorize?client_id={}&scope=bot>'.format(self.user.id)
                    await send_message(message.channel, mess)
                        
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
                    roles = '\n'.join([r.mention for r in sorted(member.roles, key=lambda x:x.position, reverse=True) if r.name != '@everyone'])
                    if roles == '': roles = '\@everyone'
                    embed.add_field(name='Roles', value=roles)

                    embed.set_author(name=member, icon_url=avatar)

                    try:
                        await message.channel.send(embed=embed)
                    except discord.errors.Forbidden:
                        pass
                
                elif command == 'ping':
                    await send_message(message.channel, 'Pong')
                
                # TWOW-Bot ready!
                elif command == 'id':  # Gets the server ID used in voting
                    if message.channel.id in self.servers:
                        await send_message(message.channel, 
                            'This mTWOW\'s identifier is `{}`'.format(self.servers[message.channel.id]))
                    else:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data. If this is an error, please contact {}.'.format(self.get_user(BOT_HOSTER)))
                elif command == 'prompt':  # Gets the current prompt
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
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
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    await send_message(message.channel, 'We are on season {}'.format(sd['season']))
                elif command == 'round':  # Get the current round number
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    await send_message(message.channel, 'We are on round {}'.format(sd['round']))
                elif command == 'vote':  # I think it makes me a hot dog. Not sure.
                    if not isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.delete()
                        await send_message(message.channel, 'Please only vote in DMs')
                        return
                    
                    if len(args) > 2 or not args[0]:
                        await send_message(message.channel, 
                            'Usage: `{}vote <TWOW id> [vote]\nUse `.id` in the channel to get the id.'.format(PREFIX))
                        return
                    
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

                            if len(responses) < 2:
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
                            m += '\n:regional_indicator_{}: {}'.format(string.ascii_lowercase[n], round['responses'][i].decode())
                            if len(m) > 1500:
                                await send_message(message.channel,m)
                                m = ''
                        if m:
                            await send_message(message.channel,m)
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
                        await send_message(message.channel, 
                            'Usage: `{}respond <TWOW id> <response>`\nUse `.id` in the channel to get the id.'.format(PREFIX))
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
                    '''
                    for role in self.get_channel(s_ids[id]).guild.roles:
                        if role.id == sd['ids']['alive']:
                            alive_role = role
                            break
                    else:
                        alive_role = None'''
                    member = self.get_channel(s_ids[id]).guild.get_member(int(message.author.id))
                    if sd['round'] > 1 and message.author.id not in sd['alive']:
                        await send_message(message.channel, 'You are unable to submit this round. Please wait for the next season.')
                        return
                    elif sd['round'] == 1 and message.author.id not in sd['alive']:
                        sd['alive'].append(member.id)
                    
                    if message.author.id in round['responses']:
                        await send_message(message.channel, '**Warning! Overwriting current response!**')
                    if len(response.split(' ')) > 10:
                        await send_message(message.channel, '**Warning! Your response looks to be over 10 words ({}).**\nThis can be ignored if you are playing a variation TWOW that doesn\'t have this limit'.format(len(response.split(' '))))
                    if len(response) > 140:
                        await send_message(message.channel, 'That is a lot of characters. Why don\'t we tone it down a bit?')
                        return
                    
                    changed = False
                    with open('banned_words.txt') as bw:
                        banned_w = bw.read().split('\n')
                    for i in banned_w:
                        if i:
                            pattern = re.compile(i, re.IGNORECASE)
                            if pattern.match(response):
                                response = pattern.sub('\\*' * len(i), response)
                                print(response)
                                changed = True
                    if changed:
                        await send_message(message.channel, '**Due to rude words, your submission has been changed to:**\n{}'.format(response))
                    
                    round['responses'][message.author.id] = response.encode('utf-8')
                    await send_message(message.channel, '**Submission recorded**')
                    
                    save_data()
                        
                # TWOW owner only commands
                elif command == 'start_voting':
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    if sd['voting']:
                        await send_message(message.channel, 'Voting is already active.')
                        return
                    roundn = sd['round']
                    seasonn = sd['season']
                    if len(sd['seasons']['season-{}'.format(seasonn)]['rounds']['round-{}'.format(roundn)]['responses']) < 2:
                        await send_message(message.channel, 'There aren\'t enough responses to start voting. You need at least 2.')
                        return
                    
                    sd['voting'] = True
                    save_data()
                    await send_message(message.channel, 'Voting has been activated.')
                    return
                elif command == 'results':  # Woah? Results. Let's hope I know how to calculate these.. Haha. I didn't.
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
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
                    for twower in sd['alive']:
                        if twower not in round['responses']:
                            round['responses'][twower] = '*DNP*'.encode('UTF-8')
                            totals.append({'name': twower, 'borda': 0, 'votes': 1, 'raw_borda': [0]})
                    msg = '**Results for round {}, season {}:**'.format(sd['round'], sd['season'])
                    
                    await message.delete()
                    await send_message(message.channel,msg)
                    
                    eliminated = []
                    living = []
                    
                    elim = int(0.8 * len(totals))
                    if len(args) > 0 and args[0] != '':
                        nums = args[0]
                        try:
                            if nums[-1] == '%':
                                elim = len(totals)*(100-int(nums[:-1]))//100
                            else:
                                elim = len(totals) - int(nums)
                        except ValueError:
                            await send_message(message.channel, '{} doesn\'t look like a number to me.'.format(nums))
                            return
                    
                    for n, v in list(enumerate(totals))[::-1]:
                        score = f(v)
  
                        mean = sum(v['raw_borda']) / len(v['raw_borda'])
                        variance = sum((i - mean) ** 2 for i in v['raw_borda']) / len(v['raw_borda'])
                        stdev = variance ** 0.5
                    
                        user = message.guild.get_member(v['name'])
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
                            

                        dead = n >= elim
                        if dead:
                            if user.id in sd['alive']:
                                sd['alive'].remove(user.id)
                            eliminated.append((name, user, v))
                        else:
                            living.append((name, user, v))
                        
                        msg = '\n{}\n{} **{}{} place**: *{}*\n**{}** ({}% σ={})'.format('=' * 50, ':coffin:' if dead else ':white_check_mark:', n + 1, symbol, round['responses'][v['name']].decode('utf-8'), name, builtins.round(score, 2), builtins.round(stdev, 2))

                        await asyncio.sleep(len(totals) - n / 2)
                        await send_message(message.channel,msg)  
                    user = message.guild.get_member(totals[0]['name'])
                    if user is not None:
                        name = user.mention
                    else:
                        name = str(v['name'])
                    msg = '{}\nThe winner was {}! Well done!'.format('=' * 50, name)
                    await send_message(message.channel,msg)  
                    
                    await send_message(message.channel,
                        'Sadly though, we have to say goodbye to {}.'.format(', '.join([i[0] for i in eliminated])))
                    '''
                    for role in message.guild.roles:
                        if role.id == sd['ids']['alive']:
                            alive_role = role
                            break
                    else:
                        alive_role = None
                    for role in message.guild.roles:
                        if role.id == sd['ids']['dead']:
                            dead_role = role
                            break
                    else:
                        dead_role = None'''
                    
                    # Do all the round incrementing and stuff.
                    if len(totals) - len(eliminated) <= 1:
                        await send_message(message.channel,'**This season has ended! The winner was {}!**'.format(name))
                        sd['round'] = 1
                        sd['season'] += 1
                    else:
                        sd['round'] += 1
                        await send_message(message.channel,'**We\'re now on round {}!**'.format(sd['round']))
                        
                    if 'season-{}'.format(sd['season']) not in sd['seasons']:
                        sd['seasons']['season-{}'.format(sd['season'])] = {'rounds':{}}
                        sd['alive'] = []
                    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
                        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
                    
                    sd['voting'] = False
                    
                    save_data()
                    
                    # Oh yeah, and kill off dead people
                    '''
                    if alive_role is not None and dead_role is not None:
                        if message.guild.large:
                            await self.request_offline_members(message.channel)
                        for e in eliminated:
                            if e[1] is not None:
                                if alive_role in e[1].roles:
                                    await e[1].remove_roles(alive_role, reason='Contestant eliminated')
                                    if dead_role is not None:
                                        await e[1].add_roles(dead_role, reason='Contestant eliminated')
                                                
                        
                        alive_r = None
                        
                        for member in message.guild.members:
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
                        '''
                elif command == 'responses':  # List all responses this round
                    id = None
                    if len(args) > 0 and args[0] != '':
                        s_ids = {i[1]:i[0] for i in self.servers.items()}
                        if args[0] not in s_ids:
                            await send_message(message.channel, 'I can\'t find any mTWOW under the name `{}`.'.format(id.replace('`', '\\`')))
                            return
                        id = s_ids[args[0]]
                    else:
                        if message.channel.id not in self.servers:
                            await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                            return
                        id = message.channel.id
                        
                    if self.server_data[id]['owner'] != message.author.id:
                        return
                        
                    sd = self.server_data[id]
                    
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
                            await send_message(message.author,m)
                            m = ''
                    if m:
                        await send_message(message.author,m)
                    if isinstance(message.channel, discord.TextChannel):
                        await send_message(message.channel,':mailbox_with_mail:')
                elif command == 'register':  # Setup channel initially
                    if message.channel.id in self.servers:
                        owner = self.get_user(self.server_data[message.channel.id]['owner'])
                        if owner is not None:
                            await send_message(message.channel, 'This channel is already setup. The owner is {}.'.format(owner.name.replace('@', '@\u200b')))
                        else:
                            await send_message(message.channel, 
                                'I can\'t find the owner of this mTWOW. Please contact {} to resolve this.'.format(self.get_user(BOT_HOSTER)))
                    else:
                        if not message.channel.permissions_for(message.author).manage_channels:#if user can manage that channel
                            return
                        bot_perms = message.channel.permissions_for(message.guild.get_member(self.user.id))
                        if not (bot_perms.send_messages and bot_perms.read_messages): #add any other perms you can think of
                            return
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
                            s['alive'] = []
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
                        
                            await send_message(message.channel, 
                                'Woah! I just set up a whole mTWOW for you under the name `{}`'.format(
                                    raw_args.replace('@', '@\u200b').replace('`', '\\`')))
                        else:
                            await send_message(message.channel, 'Usage: `{}register <short identifier>'.format(PREFIX))
                
                elif command == 'setup':  # Set congifs
                    pass
                    '''
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
                    '''
                elif command == 'show_config':
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                        
                    if self.server_data[message.channel.id]['owner'] != message.author.id:
                        return
                    
                    with open('./server_data/{}.yml'.format(message.channel.id), 'rb') as server_file:
                        await message.channel.send(file=discord.File(server_file))
                elif command == 'set_prompt':  # Summon unicorns
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
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
                
                elif command == 'transfer':
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                    
                    sd = self.server_data[message.channel.id]
                    if sd['owner'] != message.author.id:
                        return
                    
                    if len(message.mentions) == 0:
                        await send_message(message.channel, 'Usage: `{}transfer <User>`'.format(PREFIX))
                        return
                    
                    def check(m):
                        return m.channel == message.channel and m.author == message.author and m.content[0].lower() in ['y','n']
                    
                    await send_message(message.channel, 
                        'You are about to transfer your mtwow to {}. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.'.format(message.mentions[0].name))
                    resp = None
                    try:
                        resp = await self.wait_for('message', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        await send_message(message.channel, 'Transfer Cancelled.')
                        return
                    
                    if resp.content[0].lower() != 'y':
                        await send_message(message.channel, 'Transfer Cancelled.')
                        return

                    sd['owner'] = message.mentions[0].id
                    save_data()
                    await send_message(message.channel, 'MTWOW has been transfered to {}.'.format(message.mentions[0].name))
                    
                elif command == 'delete':
                    if message.channel.id not in self.servers:
                        await send_message(message.channel, 'There isn\'t an entry for this mTWOW in my data.')
                        return
                    
                    if sd['owner'] != message.author.id:
                        return
                    
                    def check(m):
                        return m.channel == message.channel and m.author == message.author and m.content[0].lower() in ['y','n']
                    
                    await send_message(message.channel, 
                        'You are about to delete your mtwow. Are you 100 percent, no regrets, absolutely and completely sure about this? (y/N) Choice will default to no in 60 seconds.')
                    resp = None
                    try:
                        resp = await self.wait_for('message', check=check, timeout=60)
                    except asyncio.TimeoutError:
                        await send_message(message.channel, 'Deletion Cancelled.')
                        return
                    
                    if resp.content[0].lower() != 'y':
                        await send_message(message.channel, 'Deletion Cancelled.')
                        return
                    
                    save_archive(message.channel.id)
                    self.servers.pop(message.channel.id, None)
                    self.server_data.pop(message.channel.id,None)
                    save_data()
                    await send_message(message.channel, 'MTWOW has been deleted.')
                    

    def start_bot(self):
        self.run(TOKEN)


# .replace('@', '@\u200b')
        
if __name__ == '__main__':
    b = Bot()
    b.start_bot()
