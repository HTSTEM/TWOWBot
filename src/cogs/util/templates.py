def round():
    '''Generates a new round'''
    r = {
        'alive':[], 
        'prompt': None, 
        'responses': {}, 
        'slides': {}, 
        'votes': [],
        'votetimer':None,
        'restimer':None,
        }
    return r

def twow():
    '''Generates a new twow'''
    t = {}
    t['owner'] = None
    t['round'] = 1
    t['season'] = 1
    t['voting'] = False
    t['canqueue'] = False
    t['queue'] = []
    t['elim'] = '20%'
    t['hosttimer'] = None
    t['words'] = 10
    t['blacklist'] = []
    t['queuetimer'] = {
        'prompt':None,
        'voting':None,
        'results':None,
        }
    t['seasons'] = {
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
    return t
