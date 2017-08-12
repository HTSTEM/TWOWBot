round = {
        'alive':[], 
        'prompt': None, 
        'responses': {}, 
        'slides': {}, 
        'votes': [],
        'votetimer':None,
        'restimer':None,
        }

twow = {}
twow['owner'] = None
twow['round'] = 1
twow['season'] = 1
twow['voting'] = False
twow['canqueue'] = False
twow['queue'] = []
twow['elim'] = '20%'
twow['hosttimer'] = None
twow['words'] = 10
twow['blacklist'] = []
twow['queuetimer'] = {
    'prompt':None,
    'voting':None,
    'results':None,
    }
twow['seasons'] = {
    'season-1':
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
