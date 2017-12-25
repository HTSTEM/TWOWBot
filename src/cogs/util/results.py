import builtins

SUPERSCRIPT = ['ˢᵗ', 'ᶮᵈ', 'ʳᵈ', 'ᵗʰ']

def count_votes(round):
    def f(v):
        perc = (v['borda'] / v['votes'])
        stdv = (sum((i - perc) ** 2 for i in v['raw_borda']) / len(v['raw_borda']))**0.5
        return (perc, -stdv)

    totals = {}
    for r in round['responses']:
        totals[r] = {'borda': 0, 'votes': 0, 'raw_borda': []}

    vote_weights = {}

    for vote in round['votes']:
        if vote['voter'] not in vote_weights:
            vote_weights[vote['voter']] = 0
        vote_weights[vote['voter']] += 1
    for i in vote_weights:
        vote_weights[i] = 1 / vote_weights[i]

    for vote in round['votes']:
        count = len(vote['vote']) - 1
        for n, v in enumerate(vote['vote']):
            try: score = 100 * (count - n) / count
            except ZeroDivisionError: score = 50
            totals[v]['borda'] += score * vote_weights[vote['voter']]
            totals[v]['votes'] += vote_weights[vote['voter']]
            totals[v]['raw_borda'].append(score * vote_weights[vote['voter']])
        '''
        not_voted = 0
        for i in totals:
            if i not in vote['vote']:
                not_voted += 1

        for v in totals:
            if v not in vote['vote']:
                score = sum(range(0, not_voted)) / not_voted
                score /= count

                totals[v]['borda'] += score * vote_weights[vote['voter']]
                totals[v]['votes'] += vote_weights[vote['voter']]
                totals[v]['raw_borda'].append(score * vote_weights[vote['voter']] * 100)
        '''
    totals = [{'name': i[0], **i[1]} for i in totals.items()]

    if abs(sum(i['borda'] / i['votes'] for i in totals) / len(totals) - 50) > 0.2:
        print(sum(i['borda'] / i['votes'] for i in totals) / len(totals))
        print('Weeeeeee-Woooooooo! Percentiles don\'t average to 50%.')
        print('Here are the votes cast for debugging:')


    totals.sort(key=f, reverse=True)

    return totals

def format_msg(n, response, score, stdev, dead):
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

    return '\n{}\n{} **{}{} place**: {}\n**{}** ({}% σ={})'.format(
        '=' * 50,
        ':skull_crossbones:' if (dead and n != 0) else ':white_check_mark:',
        n + 1, symbol, response,
        '{}',
        builtins.round(score, 2),
        builtins.round(stdev, 2)
    )

def get_results(totals, elim, round):
    def f(v):
        try:
            perc = v['borda'] / v['votes']
            stdv = (sum((i - perc) ** 2 for i in v['raw_borda']) / len(v['raw_borda']))**0.5
        except ZeroDivisionError:
            perc = 50
            stdv = 0
        return (perc, stdv)

    n = 0
    if len(totals) == 1:
        twower = list(totals.values())[0]
        return [(
            format_msg(n, round['responses'][twower].decode('utf-8'), 50, 0, False),
            False, twower, n
        )]
    for n, v in list(enumerate(totals)):
        score, stdev = f(v)
        dead = n >= elim

        # :blobeyes:
        msg = format_msg(n, round['responses'][v['name']].decode('utf-8'), score, stdev, dead)
        yield (msg, dead, v['name'], n)

    alive = round['alive']
    for twower in alive:
        if twower not in round['responses']:
            n += 1
            yield (format_msg(n, '*DNP*', 0, 0, True), True, twower, n)


