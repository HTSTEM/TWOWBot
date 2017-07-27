import random
import argparse
import os
import json#gotta switch to yaml
import csv
import configparser
from PIL import Image, ImageDraw, ImageFont
from .textTools import wrap_text

encoding = 'UTF-8'
font_path = ''
    
font = ImageFont.truetype(font_path,30)

preserve=True
use_old = False
def parse_args(keylist):
    global preserve
    global use_old
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument("-i", "--iterations", nargs='?', type=int, const=20, default=10, help='number of voting screens')
    parser.add_argument("-r", "--responses_to_use", nargs='+', default=[], type=int, 
                        help='specify which responses you want to make voting screens for, use the number of responses, first response is 0')
    parser.add_argument("-p","--no_preserve",action='store_false',help='don\'t keep old slides')
    parser.add_argument("-f","--use_old",action='store_true',help='Use existing dict.json to make voting slides')
    args = parser.parse_args()
    path = args.input
    its=args.iterations
    preserve=args.no_preserve
    use_old=args.use_old
    submissions = []
    with open('./twows/{}/responses.csv'.format(path),'r',encoding=encoding) as csvfile:#read responses
        reader = csv.reader(csvfile)
        for row in reader:
            submissions.append(row[1])

    submissionCount = len(submissions)
    
    return (path,its,submissions,keylist,submissionCount,args.responses_to_use)
    
def create_random_order(submissions,its,submissionCount,to_use):
    voteList = []
    if len(to_use)==0:
        for i in range(int(10*its/len(submissions))+1):
            randomSubmissionOrder = list(range(submissionCount))
            random.shuffle(randomSubmissionOrder)
            voteList.append(randomSubmissionOrder)
    elif len(to_use)<10:
        for i in range(its):
            randomSubmissionOrder = to_use+random.sample(list(range(submissionCount)),10-len(to_use))
            random.shuffle(randomSubmissionOrder)
            voteList.append(randomSubmissionOrder)
    else:
        for i in range(int(10*its/len(to_use))+1):
            randomSubmissionOrder = list(range(len(to_use)))
            random.shuffle(randomSubmissionOrder)
            voteList.append(randomSubmissionOrder) 
        
    return voteList

def count_words(text):
    return text.strip().count(' ')+1
            

def draw_screens(keylist,path,its,voteList,submissionCount,submissions):
    global preserve
    screenDict = {}
    if preserve:
        try:
            screenDict = json.load(open('./twows/{}/dict.json'.format(path)))
        except:
            screenDict = {}
    top = len(screenDict)
    voteNumber = 0
    text_writer = open('./twows/{}/ballots.txt'.format(path),'w')
    for iteration in range(its):

        base = Image.open('./resources/base.png').convert('RGB')
        drawer = ImageDraw.Draw(base)
        existingEntries = []
        
        word = keylist[iteration].upper()

        while word in screenDict.keys():
            keylist.pop(iteration)
            word = keylist[iteration].upper()
            
        w,h = drawer.textsize(word,font)
        drawer.rectangle([1462,16,1430-w,53+h],fill=(255,214,0))
        drawer.text((1448-w, 30), word, font=font, fill="black")
        
        text_writer.write(word+'\n\n')
        
        for i in range(10):
            
            #ensures all submissions are displayed
            submissionNumber=0
            if use_old:
                submissionNumber = voteList[iteration][i]
            else:
                submissionNumber = voteList[int(voteNumber/submissionCount)][voteNumber%submissionCount] 
            while submissionNumber in existingEntries:
                voteList[int(voteNumber/submissionCount)].remove(submissionNumber)
                voteList[int(voteNumber/submissionCount)].append(submissionNumber)
                submissionNumber = voteList[int(voteNumber/submissionCount)][voteNumber%submissionCount]
                
            response = wrap_text(submissions[submissionNumber],1100,font,drawer)
            drawer.text((100,70.875*i+60-drawer.textsize(response,font)[1]/2), response, font=font, fill=(0,0,0))
            distance = 130+drawer.textsize(response,font)[0]
            
            wordCount = count_words(response)
                    
            if wordCount >10:
                drawer.text((distance,int(71.5*i)+42), str(wordCount), font=font, fill=(255,0,0))#blue
            else:
                drawer.text((distance,int(71.5*i)+42), str(wordCount), font=font, fill=(30,30,255))#red
            
            existingEntries.append(submissionNumber)
            ballot_line = ':regional_indicator_{}: {} ({})\n'.format(chr(i+97),submissions[submissionNumber],wordCount)
            text_writer.write(ballot_line)
            
            voteNumber+=1
            
        screenDict[word]=list(existingEntries)
        base.save('./twows/{}/voteScreens/{}.png'.format(path,iteration+top))
        text_writer.write('\n\n\n\n\n')
     
    if not use_old:
        open('./twows/{}/dict.json'.format(path),'w').write(json.dumps(screenDict))

    
def main():
    global preserve
    keylist = open('./resources/words.txt','r').read().split('\n')
    path,its,submissions,keylist,submissionCount,to_use = parse_args(keylist)
    if not use_old:
        random.shuffle(keylist)
        voteList = create_random_order(submissions,its,submissionCount,to_use)
        os.makedirs('./twows/{}/voteScreens'.format(path), exist_ok=True)
        draw_screens(keylist,path,its,voteList,submissionCount,submissions)
    else:
        try:
            slides = json.load(open('./twows/{}/dict.json'.format(path),'r'))
        except:
            pass
        preserve = False
        keylist = list(slides.keys())
        voteList = list(slides.values())
        os.makedirs('./twows/{}/voteScreens'.format(path), exist_ok=True)
        draw_screens(keylist,path,len(slides),voteList,submissionCount,submissions)
    
    
if __name__ == '__main__':
    main()
