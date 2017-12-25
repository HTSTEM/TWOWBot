import asyncio
import datetime
import discord

from . import results, twow_helper, templates


async def start_voting(bot, channel):
    sd = bot.server_data[channel.id]

    if sd['voting']:
        await bot.send_message(channel, 'Voting is already active.')
        return

    round = sd['seasons'][f'season-{sd["season"]}']['rounds'][f'round-{sd["round"]}']
    if len(round['responses']) < 2:
        await bot.send_message(channel, 'There aren\'t enough responses to start voting. You need at least 2.')
        if round['votetimer'] is not None:
            await bot.send_message(channel, 'Waiting for more responses.')
            round['votetimer'] = 'waiting'
            bot.save_data()
        return

    sd['voting'] = True
    round['votetimer'] = None
    if sd['queuetimer']['results'] is not None and round['restimer'] is None:
        import datetime
        round['restimer'] = datetime.datetime.utcnow()+sd['queuetimer']['results']
    bot.save_data()
    await bot.send_message(channel, 'Voting has been activated.')


async def do_results(bot, channel, guild, nums='', message=None):
    sd = bot.server_data[channel.id]
    round = sd['seasons'][f'season-{sd["season"]}']['rounds'][f'round-{sd["round"]}']

    if not sd['voting']:
        await bot.send_message(channel, 'Voting hasn\'t even started yet...')
        return

    if 'season-{}'.format(sd['season']) not in sd['seasons']:
        sd['seasons']['season-{}'.format(sd['season'])] = {}
    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:
        sd['seasons'][f'season-{sd["season"]}']['rounds'][f'round-{sd["round"]}'] = dict(templates.round())

    voted_ons = set()
    for vote in round['votes']: voted_ons |= set(vote['vote'])
    if set(round['responses']) != voted_ons:
        await bot.send_message(channel, 'Not every response has been voted on yet!')
        if round['restimer'] is not None:
            await bot.send_message(channel, 'Waiting for more votes.')
            round['restimer'] = 'waiting'
            bot.save_data()
        return

    totals = results.count_votes(round)
    msg = '**Results for round {}, season {}:**'.format(sd['round'], sd['season'])
    if message is not None:
        try: await message.delete()
        except discord.Forbidden: pass
    eliminated = []
    living = []
    if nums == '': nums = sd['elim']
    try:
        if nums[-1] == '%':
            elim = len(totals)*(100-int(nums[:-1]))//100
        else:
            elim = len(totals) - int(nums)
    except ValueError:
        await bot.send_message(channel, '{} isn\'t in a valid format.'.format(nums))
        return
    round['restimer'] = None
    await bot.send_message(channel, msg)
    votec = len(round['votes'])
    voterc = len(set([v['voter'] for v in round['votes']]))
    votest = '{} vote'.format(votec)
    if votec != 1: votest += 's'
    voterst = '{} voter'.format(voterc)
    if voterc != 1: voterst += 's'

    await asyncio.sleep(1)
    await bot.send_message(channel, '{} submitted {}.'.format(voterst, votest))

    for msg, dead, uid, n in results.get_results(totals, elim, round):
        user = guild.get_member(uid)
        if user is not None:
            name = user.mention
        else:
            name = str(uid)

        if dead:
            eliminated.append((name, uid))
        else:
            living.append((name, uid))

        if dead: await asyncio.sleep(1)
        else: await asyncio.sleep(1 + 5 * n / elim)
        await bot.send_message(channel, msg.format(name))

    # Winner/loser stuff
    try:
        user = guild.get_member(totals[0]['name'])
    except IndexError:
        await bot.send_message(channel, 'Somehow you did results with no one or something like that.')
        return

    if user is not None:
        name = user.mention
    else:
        name = str(totals[0]['name'])
    msg = '{}\nThe winner was {}! Well done!'.format('=' * 50, name)
    await bot.send_message(channel, msg)
    if user: round['winner'] = user.id

    if eliminated:
        await bot.send_message(
            channel,
            'Sadly though, we have to say goodbye to {}.'.format(', '.join([i[0] for i in eliminated]))
        )
    else:
        await bot.send_message(
            channel,
            'You all lived on. I would say well done, but The elimination threshold was probably at 0.'
        )
    advance = False

    # Do all the round incrementing and stuff.
    if len(totals) - len(eliminated) <= 1:
        await bot.send_message(channel, f'**This season has ended! The winner was {name}!**')
        sd['seasons']['season-{}'.format(sd['season'])]['winner'] = user.id
        sd['round'] = 1
        sd['season'] += 1
        await bot.send_message(channel, '**We\'re now on season {}!**'.format(sd['season']))
        if sd['canqueue']:
            advance = True
    else:
        sd['round'] += 1
        await bot.send_message(channel, '**We\'re now on round {}!**'.format(sd['round']))
        if sd['canqueue'] and len(sd['queue']) > 0:
            if sd['queuetimer']['prompt'] is not None:
                sd['hosttimer'] = datetime.datetime.utcnow()+sd['queuetimer']['prompt']

    if 'season-{}'.format(sd['season']) not in sd['seasons']:  # new season
        sd['seasons'][f'season-{sd["season"]}'] = {'rounds': {}}
        living = []
    if 'round-{}'.format(sd['round']) not in sd['seasons']['season-{}'.format(sd['season'])]['rounds']:  # new round
        sd['seasons'][f'season-{sd["season"]}']['rounds'][f'round-{sd["round"]}'] = dict(templates.round())

    sd['seasons'][f'season-{sd["season"]}']['rounds'][f'round-{sd["round"]}']['alive'] = [t[1] for t in living]

    if advance:
        await twow_helper.next_host(bot, channel, sd)

    sd['voting'] = False

    bot.save_data()
