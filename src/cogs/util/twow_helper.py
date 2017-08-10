import re
import random
import datetime

from cogs.util import timed_funcs

RESPONSES_PER_SLIDE = 10

def new_twow(db, identifier, channel, owner):
    s = {}
    s['owner'] = owner
    s['round'] = 1
    s['season'] = 1
    s['voting'] = False
    s['canqueue'] = False
    s['queue'] = []
    s['elim'] = '20%'
    s['hosttimer'] = None
    s['queuetimer'] = {
        'prompt':None,
        'voting':None,
        'results':None,
        }
    s['seasons'] = {'season-1':
                    {'rounds':
                        {'round-1':
                        {
                        'alive':[],
                        'prompt': None,
                        'responses': {},
                        'slides': {},
                        'votes': [],
                        'votetimer':None,
                        'restimer':None,
                        }
                        }
                    }
                    }
    
    db.server_data[channel] = s
    db.servers[channel] = identifier
    db.save_data()
    
def respond(db, id, responder, response): # 1 = no twow, 3 = voting started, 5 = no prompt, 7 = dead, 9 = too many chars, 11 = too many words
    s_ids = {i[1]:i[0] for i in db.servers.items()}
    if id not in s_ids:
        return (1, '')
    
    sd = db.server_data[s_ids[id]]
    
    if sd['voting']:
        return (3, '')
    
    if 'season-{}'.format(sd['season']) not in sd['seasons']:
        sd['seasons']['season-{}'.format(sd['season'])] = {}
    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
        sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])] = {'prompt': None, 'responses': {}, 'slides': {}, 'votes': []}
    
    round = sd['seasons']['season-{}'.format(sd['season'])]['rounds']['round-{}'.format(sd['round'])]
    
    if round['prompt'] is None:
        return (5, '')

    if sd['round'] > 1 and responder not in round['alive']:
        return (7, '')
    elif sd['round'] == 1 and responder not in round['alive']:
        round['alive'].append(responder)
        
    success = 0
    if responder in round['responses']:
        success += 2
    if sd['words'] > 0 and len(response.split(' ')) > sd['words']:
        return (11, (sd['words'], len(response.split(' '))))
    if len(response) > 140:
        return (9, '')
    
    if sd['blacklist']:
        changed = False
        with open('static_data/banned_words.txt') as bw:
            banned_w = bw.read().split('\n')
        for i in banned_w:
            if i:
                pattern = re.compile('\\b' + re.escape(i) + '\\b', re.IGNORECASE)
                if pattern.findall(response):
                    response = pattern.sub('\\*' * len(i), response)
                    changed = True
        if changed:
            success += 8
    
    round['responses'][responder] = response.encode('utf-8')
    db.save_data()
    if round['votetimer'] == 'waiting' and len(round['responses']) > 1:
        import asyncio
        if type(sd['queuetimer']['results']) == datetime.timedelta:
            round['restimer'] = datetime.utcnow() + sd['queuetimer']['results']
        asyncio.ensure_future(timed_funcs.start_voting(db, db.get_channel(s_ids[id])))
        
    return success, response

def create_slides(db, round, voter):
# Sort all responses based off their number of votes
    responses = [[i, 0] for i in round['responses']]
    for i in responses:
        if i[0] == voter:
            responses.remove(i)
    for vote in round['votes']:
        # Each vote is a list of user IDs going from best to worst
        for i in vote['vote']:
            for r in responses:
                if r[0] == i:
                    r[1] += 1
                    break
            else:
                if i != voter:
                    responses.append([i, 1])
    responses.sort(key=lambda x:x[1])

    if len(responses) < 2:
        return False
    
    # ~~Calculate the nubmer of responses per slide~~ Global at start of file.
    # Take that many items from the list of responses.
    
    slide = responses[:RESPONSES_PER_SLIDE]
    slide = [i[0] for i in slide]
    random.shuffle(slide)
    
    # Save as a slide.
    round['slides'][voter] = slide
    
    db.save_data()
    return True

def get_delta(times):
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    current = ''
    for c in times:
        if c == 'd':
            days = int(current)
        elif c == 'h':
            hours = int(current)
        elif c == 'm':
            minutes = int(current)
        elif c == 's':
            seconds = int(current)
        else:
            current += c
            continue
        current = ''
    
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return delta

async def next_host(bot, channel, sd):
    prev = sd['queue'].pop(0)
    name = channel.guild.get_member(prev).mention
    sd['hosttimer'] = None
    await bot.send_message(channel, '{} is no longer hosting!'.format(name))
    if len(sd['queue']) > 0:
        if sd['queuetimer']['prompt'] != None:
            sd['hosttimer'] = datetime.datetime.utcnow()+sd['queuetimer']['prompt']
        if sd['queuetimer']['voting'] != None:
            votetimer = datetime.datetime.utcnow()+sd['queuetimer']['voting']
        if sd['queuetimer']['results'] != None:
            restimer = datetime.datetime.utcnow()+sd['queuetimer']['results']
        name = channel.guild.get_member(sd['queue'][0]).mention
        await bot.send_message(channel, '{} is now hosting!'.format(name))
    
    
