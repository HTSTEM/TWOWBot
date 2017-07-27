import ast
import argparse
import statistics
import textwrap
import csv
import json
import os
import time
import configparser
from PIL import Image, ImageDraw, ImageFont, ImageColor
from .voteConverter import convert
from .booksonaGen import make_book
from .textTools import wrap_text, simplify

config = configparser.ConfigParser()
config.read('config.ini')
encoding = config['DEFAULT']['Encoding']
font_path = config['DEFAULT']['Font']

font = ImageFont.truetype(font_path,13)
bigfont =  ImageFont.truetype(font_path,30)
smallfont = ImageFont.truetype(font_path,13)

id_dict = json.loads(open('bot_data/people.json','r').read())
for key, value in id_dict.items():
    id_dict[key]=value['name']

should_draw=True
to_omit = []

def parse_args():
    global should_draw
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument("-e", "--perc_elim", nargs='?', type=int, const=-1, default=20, 
                        help='Percentage of contestants eliminated, set to negative number to specify number of contestants')
    parser.add_argument("-t", "--num_gold", nargs='?', type=int, const=5, default=1, help='Number of contestants to place in gold highlighting')
    parser.add_argument('-i', '--omit_image', action='store_false', help='Use this flag to not draw image')
    parser.add_argument('-o', '--omit_response', nargs='+', type=int, default=[], 
                        help='Use this flag to omit a response from the voting.')
    args = parser.parse_args()
    path = args.input
    
    votes = convert(path)
    prompt = open('./twows/{}/prompt.txt'.format(path),'r').read().split('\n')[0]
    scores = []
    twowers=set()
    counter=0
    with open('./twows/{}/responses.csv'.format(path),'r',encoding=encoding) as csvfile:#read responses
        reader = csv.reader(csvfile)
        for row in reader:
            if counter in args.omit_response:
                to_omit.append(row[1])
            counter+=1
            #scoredata format [twower, response, votes/mean, count, boost, final, stdev, votegraph] (probably outdated)
            name = simplify(row[0])
            twowers.add(name)
            try:
                scores.append([name,row[1],[],0,int(row[2]),0,0,0,[0 for i in range(10)],[]])
            except:
                scores.append([name,row[1],[],0,0,0,0,0,[0 for i in range(10)],[]])
    
    twowers = list(twowers)
    twower_count = len(twowers)
    should_draw=args.omit_image
    top_number = args.num_gold #chart coloring ranges
    elim_number=0
    
    if int(args.perc_elim) < 0:
        elim_number = -args.perc_elim
    else:
        elim_number = round(args.perc_elim*len(twowers)/100)
    
    return (path, prompt, scores, votes, twowers, twower_count, top_number, elim_number)
        
    
def draw_header(prompt, base, drawer,scores):
    prompt = wrap_text(prompt,1000,bigfont,drawer)
    header_height = drawer.textsize(prompt,bigfont)[1]+35
    base = Image.new('RGBA',(1368,header_height+int(67/2*len(scores))),color=(255,255,255,255))
    drawer = ImageDraw.Draw(base)
    base.paste(Image.open('./resources/header.png'),(0,header_height-40))
    drawer.text((15,0),prompt,font=bigfont, fill=(0,0,0,255))
    
    return (prompt, base, drawer, header_height)
    

def process_votes(votes, scores, path):    

    for user_vote in votes:#maps votes to responses
        weight = 1
        if len(user_vote)>1:
            weight = 2/len(user_vote)
        for vote in user_vote:
            percentage = 100.0
            placing = 0
            for resp_num in vote[:-1]:
                scores[resp_num][2].append(percentage*weight)#vote and weight
                scores[resp_num][3] += weight#division stuff
                scores[resp_num][8][placing] += 1#histogram
                scores[resp_num][9].append(percentage)#more histogram?
                
                percentage -= 100/9
                placing += 1
                if percentage < 0:#screw floating point numbers
                    percentage = 0

            try:
                
                unvtd = len(vote[-1])-1
                percentage_left = 50*unvtd/9
                print(vote)
                print(percentage_left)
                for resp_num in vote[-1]:
                    scores[resp_num][2].append(-percentage_left*weight)#negative as a flag so it doesn't count as a vote
                    scores[resp_num][3] += weight

            except Exception:
                print('hi')
            

    for scoredata in scores:
        scoredata = calc_stats(scoredata)
        
        
    mergeSort(scores)#sorts from best to worst. Mergesort for best worst case    
    return scores
    
def write_csv(scores, path):
    with open('./twows/{}/results.csv'.format(path), 'w',encoding=encoding) as result_file:
        writer = csv.writer(result_file,lineterminator='\n')
        writer.writerow(['Twower','ID','Response','Subtotal','Boost','Total','Standard Deviation','Votes','Distribution'])
        writer.writerow([])
        for scoredata in scores:
            name = ''
            try:
                name = id_dict[scoredata[0]]
            except KeyError:
                name = scoredata[0]
            writer.writerow([name]+scoredata[0:1]+scoredata[1:3]+scoredata[4:8]+[scoredata[-1]])
    
def calc_stats(scoredata):#calculate stats, dm if you want more
    scoredata[7]=len([vote for vote in scoredata[2] if vote >=0])
    #print(scoredata[2])
    votes = list(abs(vote) for vote in scoredata[2])
    scoredata.append(votes)
    try:
        scoredata[2] = sum(votes)/scoredata[3]
        '''
        if scoredata[0].startswith('hanss314'):
            scoredata[2]=1000
        '''
    except:
        name = ''
        try:
            name = id_dict[scoredata[0]]
        except KeyError:
            name = scoredata[0]
   
        print('\"{}\" by {} was not voted for'.format(scoredata[1],name))
        
        scoredata[2] =0
        
    scoredata[5] = scoredata[2] + scoredata[4]
        
    try:
        scoredata[6] = statistics.stdev(scoredata[9])
    except:
        scoredata[6] = 0
            
    return scoredata
        
def draw_rankings(scores, top_number, elim_number,twower_count,base,drawer,header_height,twowers):#this one is a bit of a mess
    backgroundCol=0
    addBackground=0
    ranking=1
    twower_responses_count = {}
    
    for i in range(len(scores)):    
        twower, response, subt, boost, standev, vote_count = scores[i][0], scores[i][1], scores[i][2], scores[i][4], scores[i][6], sum(scores[i][8])
        if response in to_omit:
            continue
        twower = twower.replace("'",'')
        name = ''
        try:
            name = id_dict[twower]
        except KeyError:
            name=twower
 
        if ranking == (top_number+1):#change background depending on ranking
            backgroundCol = 1
            addBackground = 0
        elif ranking == (twower_count-elim_number+1) and twower in twowers:
            backgroundCol = 2
            addBackground = 0
            
        if (addBackground % 2) ==0:#only needs extra stuff added every two twowers
            if backgroundCol==0:
                base.paste(Image.open('./resources/top.png'),(0,int(67/2*i)+header_height))
            elif backgroundCol==1:
                base.paste(Image.open('./resources/normal.png'),(0,int(67/2*i)+header_height))
            elif backgroundCol==2:
                base.paste(Image.open('./resources/eliminated.png'),(0,int(67/2*i)+header_height))
        
        try:
            if not os.path.isfile('./booksonas/'+name+'.png'):
                make_book(name,'./booksonas/')
        except Exception as e:
            print(e)
        
        try:#attempt to add booksona
            booksona = Image.open('./booksonas/'+name+'.png')
            booksona.thumbnail((32,32),Image.BICUBIC)
            base.paste(booksona,(330,int(67/2*i)+header_height),booksona)
        except:
            pass
            
            
        rank_width = 70
        draw_double = False
        if twower in twowers:#handles multiple submissions
            twowers.remove(twower)
            twower_responses_count[twower]=1
            ranking_string = ''
            if ranking % 10 == 1:
                ranking_string = str(ranking)+'st'
            elif ranking % 10 == 2:
                ranking_string = str(ranking)+'nd'
            elif ranking % 10 == 3:
                ranking_string = str(ranking)+'rd'
            else:
                ranking_string = str(ranking)+'th'
                
            drawer.text((15,int(67/2*i+7)+header_height),ranking_string,font=font,fill=(0,0,0,255))
            rank_width = 30 + drawer.textsize(ranking_string,font)[0]
            ranking += 1
            
        else:
            twower_responses_count[twower]+=1
            draw_double = True
                
        twower_str = ''
        
        if draw_double:
            twower_str = (name + '[{}]'.format(twower_responses_count[twower]))
        else:
            twower_str = name
        
        if drawer.textsize(twower_str,font)[0] > 255: #draws twower name
            twower_str = wrap_text(twower_str,255,smallfont,drawer)
            drawer.text((rank_width,int(67/2*i+7)+header_height),
                twower_str,font=smallfont,fill=(0,0,0,255))
                
        else:
            drawer.text((rank_width,int(67/2*i+7)+header_height),
                twower_str,font=font,fill=(0,0,0,255))
                
        if drawer.textsize(response,font)[0] > 500: #draws responses
            response = wrap_text(response,500,smallfont,drawer)
            
            if response.count('\n') == 0:
                drawer.text((370,int(67/2*i+8)+header_height),
                    response,font=smallfont,fill=(0,0,0,255))
            else:
                drawer.text((370,int(67/2*i)+header_height),
                    response,font=smallfont,fill=(0,0,0,255))
        else:
            drawer.text((370,int(67/2*i+7)+header_height),
                response,font=font,fill=(0,0,0,255))
        
        draw_stats(drawer,twower,subt,standev,boost,vote_count,header_height,i)
        draw_distr(drawer,scores[i][8],i,header_height)
        
                
        addBackground += 1
        
    return scores
    
def draw_stats(drawer,twower,subt,standev,boost,vote_count,header_height,rank):
    mean_str = ''
    if boost == 0:
        mean_str = "%.2f" % round(subt,2)+'%'
    
    else:
        mean_str = "%.2f" % round(subt,2)
        mean_str += '(+{})'.format(boost)
        mean_str += '%'        
        
    width = drawer.textsize(mean_str,font)[0]
    
    drawer.text((945-width/2,int(67/2*rank+7)+header_height),
        mean_str,font=font,fill=(0,0,0,255))
        
    stdv_str = u'\u03C3 =' + ("%.2f" % round(standev,2))+'%'
    width = drawer.textsize(stdv_str,smallfont)[0]
        
    drawer.text((1300-width/2,int(67/2*rank+2)+header_height),
        stdv_str,font=smallfont,fill=(0,0,0,255))
    
    vote_str = str(vote_count)+' vote'
    if vote_count>1:
        vote_str+='s'
        
    width = drawer.textsize(vote_str,smallfont)[0]
        
    drawer.text((1300-width/2,int(67/2*rank+17)+header_height),
        vote_str,font=smallfont,fill=(0,0,0,255))

def draw_distr(drawer,distr,rank,header_height):
    norm = normalize(distr)
    bottom = int(67/2*rank)+header_height+31
    for i in range(10):
        height = int(28*norm[i])
        left = 1025+20*i
        color = (int(255*i/9),int(255*(9-i)/9),0)
        drawer.rectangle([left,bottom,left+19,bottom-height],fill=color)
        
def normalize(values):
    divisor = max(values)
    try:
        new_list = [i/divisor for i in values]
    except:
        return values
    return new_list

def grthn(bigger, smaller):
    if abs(bigger[5]-smaller[5])<0.0001:#floating point issues
        big_norm = normalize(bigger[8])
        small_norm = normalize(smaller[8])
        return big_norm>small_norm
    else:
        return bigger[5]>smaller[5]
    
        
def mergeSort(alist):
    if len(alist)>1:
        mid = len(alist)//2
        lefthalf = alist[:mid]
        righthalf = alist[mid:]

        mergeSort(lefthalf)
        mergeSort(righthalf)

        i=0
        j=0
        k=0
        while i < len(lefthalf) and j < len(righthalf):
            if grthn(lefthalf[i],righthalf[j]):
                alist[k]=lefthalf[i]
                i=i+1
            else:
                alist[k]=righthalf[j]
                j=j+1
            k=k+1

        while i < len(lefthalf):
            alist[k]=lefthalf[i]
            i=i+1
            k=k+1

        while j < len(righthalf):
            alist[k]=righthalf[j]
            j=j+1
            k=k+1
            
def write_history(path):
    history = ['']
    try:
        with open('history.txt','r+') as hist:
            history = hist.read().split('\n')
        history=[x for x in history if x!='']
    except:
        history=['']
    if path!=history[-1]:
        with open('history.txt','a+') as hist:
            hist.write(path+'\n')    
    
def main():
    global should_draw
    start = time.time()
    print('Gathering Data')
    path, prompt, scores, votes, twowers, twower_count, top_number, elim_number = parse_args()
    
    print('Processing Scores')
    scores = process_votes(votes, scores, path)
    
    if should_draw:
        print('Drawing Image')
        base = Image.new('RGBA',(1368,1368),color=(255,255,255))
        drawer = ImageDraw.Draw(base)
        prompt, base, drawer, header_height = draw_header(prompt, base, drawer,scores)
        scores = draw_rankings(scores,top_number,elim_number,twower_count,base,drawer,header_height,twowers)
        base.save('./twows/{}/results.png'.format(path))
    
    print('Recording Data')
    write_csv(scores,path)
    write_history(path)
    end = time.time()
    
    print('Time taken {} seconds'.format(end-start))
    
    
    


if __name__=='__main__':
    main()
