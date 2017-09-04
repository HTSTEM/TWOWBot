import builtins

SUPERSCRIPT = ['ˢᵗ', 'ᶮᵈ', 'ʳᵈ', 'ᵗʰ']

def count_votes(round, alive):
    def f(v):
        perc = (v['borda'] / v['votes']) / (len(round['votes'][0]['vote']) - 1) * 100
        stdv = (sum((i - perc) ** 2 for i in v['raw_borda']) / len(v['raw_borda']))**0.5
        return (perc, -stdv)

    totals = {}
    for r in round['responses']:
        totals[r] = {'borda': 0, 'votes': 0, 'raw_borda': []}

    vote_weights = {}

    for vote in round['votes']:
        if vote['voter'] not in vote_weights:
            vote_weights[vote['voter']] = 1
        else:
            vote_weights[vote['voter']] += 1
    for i in vote_weights:
        vote_weights[i] = 1 / vote_weights[i]

    for vote in round['votes']:
        c = len(vote['vote'])
        for n, v in enumerate(vote['vote']):
            bc = c - n - 1
            totals[v]['borda'] += bc * vote_weights[vote['voter']]
            totals[v]['votes'] += vote_weights[vote['voter']]
            totals[v]['raw_borda'].append((bc * vote_weights[vote['voter']]) / (c - 1) * 100)

    totals = [{'name': i[0], **i[1]} for i in totals.items()]

    totals.sort(key=f, reverse=True)
    for twower in alive:
        if twower not in round['responses']:
            round['responses'][twower] = '*DNP*'.encode('UTF-8')
            totals.append({'name': twower, 'borda': 0, 'votes': 1, 'raw_borda': [0]})
    return totals

def get_results(totals, elim, round):
    def f(v):
        perc = (v['borda'] / v['votes']) / (len(round['votes'][0]['vote']) - 1) * 100
        stdv = (sum((i - perc) ** 2 for i in v['raw_borda']) / len(v['raw_borda']))**0.5
        return (perc, stdv)

    for n, v in list(enumerate(totals))[::-1]:
        score, stdev = f(v)

        # Formatting
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

        # :blobeyes:
        msg = '\n{}\n{} **{}{} place**: *{}*\n**{}** ({}% σ={})'.format(
            '=' * 50,
            ':skull_crossbones:' if (dead and n!=0) else ':white_check_mark:',
            n + 1, symbol, round['responses'][v['name']].decode('utf-8'),
            '{}',
            builtins.round(score, 2),
            builtins.round(stdev, 2)
            )
        yield (msg, dead, v['name'], n)
