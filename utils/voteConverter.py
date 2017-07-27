import json
import sys
import csv

def convert(path):

    keywords = json.load(open('./twows/{}/dict.json'.format(path),'r'))
    vote_strings={}
    votes = []
    final_votes = []
        
    with open('./twows/{}/votes.csv'.format(path),'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                vote_strings[row[0]].append(row[1])
            except:
                try:
                    vote_strings[row[0]] = [row[1]]
                except:
                    pass
            

    for user_vote_str in vote_strings.values():
        user_vote = []
        
        for vote in user_vote_str:
            current = vote.strip('[')
            current = current.strip('\n')
            current = current.strip(']')
            current = current.split(' ')
            user_vote.append(current)
            
        votes.append(user_vote)
        
        
    for user_vote in votes:
        final_vote = []
        for vote in user_vote:
            indexes = []
            mapping = []
            not_voted_for = []
            vote[1] = remove_dups(vote[1])
            try:
                mapping = keywords[vote[0]]
                
            except:
                continue
            order = []
            not_voted_for = list(mapping)
            for c in vote[1].upper():
                indexes.append(ord(c)-65)

            for index in indexes:
                order.append(mapping[index])
                not_voted_for.remove(mapping[index])
                
            order.append(not_voted_for)
                
            final_vote.append(order)
        final_votes.append(final_vote)
    return final_votes
    
def remove_dups(seq):
    seen = set()
    seen_add = seen.add
    unique = [x for x in seq if not (x in seen or seen_add(x))]
    final = [x for x in unique if (x in 'ABCDEFGHIJabcdefghij')]
    return ''.join(final)

if __name__ == '__main__':
    votes = convert(sys.argv[1])
    print(votes)
    open('./twows/{}/votes.json'.format(sys.argv[1]),'w').write(json.dumps(votes))
