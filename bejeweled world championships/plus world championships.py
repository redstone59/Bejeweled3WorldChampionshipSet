from ReadWriteMemory import ReadWriteMemory #install
import json
import psutil #install
from tkinter import filedialog
import os,sys
from pydbg import *
import struct
import time

p = os.path.dirname(os.path.abspath(sys.argv[0]))
questjson={}

def openchal():
    filetypes=(('JSON file', '*.json'),('All Files','*.*'))
    global questjson
    questjson = json.load(open(filedialog.askopenfilename(title="Open the challenge file",initialdir=p,filetypes=filetypes)))
    try:
        if 'challengeinfo' not in questjson.keys():
            print('Invalid json file')
            openchal()
    except:
        print('Invalid json file')
        openchal()

def findProcessIdByName(processName): #stolen straight from thisPointer's site, thanks!
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string processName
    '''
    listOfProcessObjects = []
    #Iterate over the all the running process
    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           # Check if process name contains the given name string.
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass
    return listOfProcessObjects;

def checkGameOpen():
    pluspidlist = findProcessIdByName('popcapgame1.exe')
    if len(pluspidlist) == 0:
        input("Bejeweled 3 not found, please open the game and hit the Enter key to try again.")
        checkGameOpen()
    else:
        print('Bejeweled 3 found!')
        global game
        game=ReadWriteMemory().get_process_by_name('popcapgame1.exe')
        game.open()
        #base address find here
        global addr
        addr = int(input('type funky "popcapgame1.exe"+00487F34 here: '),base=16)


def addscores():
    global finalscore
    finalscore=0
    print('---------------')
    print('Final Score:')
    for x in range (1,i):
        subscript=list(questjson)[x]
        currentquest=questjson[subscript]
        print(currentquest['objective'] + ' : ' + f"{umscores[x-1]:,}" + ' * ' + f"{currentquest['multiplier']:,}" + ' = ' + f"{mscores[x-1]:,}")
        finalscore=finalscore + mscores[x-1]
    print("FINAL SCORE : " + f"{finalscore:,}")

def checksubchal():
    global score
    global iscomplete
    iscomplete=0
    #modify miniquest goals
    if currentquest['objective']=='Balance':
        if currentquest['flag']=='value':
            goalpointer=game.read(addr+0xBE0)+0x3238
            win=currentquest['condition']/2
            game.write(goalpointer,int(win))
        if currentquest['flag']=='timed':
            goalpointer=game.read(addr+0xBE0)+0x3238
            game.write(goalpointer,34710)
            game.write(game.read(addr+0xBE0)+0x323C,9)
    if currentquest['objective']=='Stratamax':
        movepointer=game.read(addr+0xBE0)+0x323C #pointer to move counter
        game.write(movepointer,currentquest['condition'])
        game.write(movepointer-4,currentquest['condition'])
        while iscomplete==0:
            if game.read(movepointer)<=0:
                score=game.read(scpointer)
                iscomplete=1
                return
    #gem-based quests
    if currentquest['objective'] in ["Avalanche","Stratamax"]: #still need to find GemGoal
        print('yeah')
    #bomb quests
    if currentquest['objective'] in ["TimeBomb","MatchBomb"]:
        pass
    #gold rush quests
    #move-based quests
    #time-based quests
    if currentquest['objective'] in ["BuriedTreasure","GoldRush","Sandstorm","WallBlast"]:
        game.write(game.read(addr+0xBE0)+0x3238,1800) #change quest base time to 30 minutes
    #poker quests
    if currentquest['objective'] in ["Poker","PokerLimit","PokerHand","PokerSkull"]:
        if game.read(game.read(addr+0xBE0)+0x323C) != 1000: #check if miniquest id is not the one of the secret poker mode
            game.write(game.read(addr+0xBE0)+0x3958,100000) #change PokerGoal to an absurdly high number
            game.write(game.read(addr+0xBE0)+0x395C,1000) #change amount of hands remaining
            print("you're really shooting yourself in the foot here by using the quest version")
    #add extra quest option
    if currentquest['objective'] in ["Avalanche","Butterflies","ButterClear","ButterCombo","MatchBomb","TimeBomb"]:
        if 'qextra' in currentquest.keys():
            game.write(game.read(addr+0xBE0)+0x3238,currentquest['qextra'])
        elif currentquest['objective']=="Avalanche":
            game.write(game.read(addr+0xBE0)+0x3238,5) #5 gems fall as default
        elif currentquest['objective'] in ["Butterflies","ButterClear","ButterCombo"]:
            game.write(game.read(addr+0xBE0)+0x3238,1) #1 match/move as default
        elif currentquest['objective'] in ["MatchBomb","TimeBomb"]:
            game.write(game.read(addr+0xBE0)+0x3238,30) #starting number of bombs is 30 (matches/seconds)
    if currentquest['flag']=='value':
        if 'timebonus' in currentquest.keys():
            print('time bonus val')
            timescore=int(currentquest['time'])*1000
            while iscomplete==0:
                if game.read(scpointer)>=currentquest['condition']:
                    score=timescore
                    iscomplete=1
                time.sleep(0.001)
                if timescore>=1:
                    timescore=timescore-1
        else:
            print('non timebonus val')
            while iscomplete==0:
                if game.read(scpointer)>=currentquest['condition']:
                    score=game.read(scorepointer)
                    iscomplete=1
    if currentquest['flag']=='timed':
        print('timed chal')
        time.sleep(currentquest['time'])
        score=game.read(scorepointer)
        iscomplete=1
    elif currentquest['flag']=='endless':
        print('endless chal')
        input('hit enter to end i havent made a thing that does time yet')
        score=game.read(scorepointer)

def subchallenge(id):
    #find pointer
    global game
    game.open()
    scoffset=offset[id]
    if currentquest['objective'] == 'PokerHand':
        handlist=['Pair','Spectrum','Two Pair','3 of a Kind','Full House','4 of a Kind','Flush']
        scoffset[1]=int(scoffset[1],base=16)
        print(str(int(scoffset[1])))
        scoffset[1]=str(int(scoffset[1])+(4*handlist.index(currentquest['hand'])))
        scoffset[1]=str(hex(int(scoffset[1])))
    global scpointer
    scpointer=game.read(addr+int(scoffset[0],base=16))
    for m in range (1,len(scoffset)):
        scpointer=scpointer+int(scoffset[m],base=16)
    global scorepointer
    if mode[currentquest['objective']] == "Diamond Mine" or mode[currentquest['objective']] == "Quest":
        scorepointer=game.read(addr+0xBE0)+0xE00
    else:
        scorepointer=game.read(addr+0xBE0)+0xD20
    game.write(game.read(addr+0xBE0)+0xD20,0)
    game.write(game.read(addr+0xBE0)+0xE00,0)
    print('GO!')
    checksubchal()
    #score stuffs
    print(score)
    del scoffset
    mscores.append(int(score)*int(currentquest['multiplier']))
    umscores.append(int(score))

checkGameOpen()
openchal()
offset=json.load(open(p + '\\jsons\\offsets.json'))
strs=json.load(open(p + '\\jsons\\strings.json'))
aflags=json.load(open(p + '\\jsons\\allowedflags.json'))
mode=json.load(open(p + '\\jsons\\mode.json'))
mqids=json.load(open(p + '\\jsons\\miniquestids.json'))
i=0
mscores=[]
umscores=[]
for x in questjson:
    currentquest=questjson[x]
    if x=='challengeinfo': #print challenge metadata
        print(currentquest['name'] + " by " + currentquest['author'] + ".")
        print(currentquest['description'])
        if currentquest['type']=='timed':
            print(str(currentquest['time']) + 's timed challenge, ' + str(len(questjson)-1) + ' sub-challenges long.')
        else:
            print('Marathon challenge, '+ str(len(questjson)-1) + ' sub-challenges long.')
        print('')
        i+=1
        continue
    if aflags[currentquest['objective']].count(currentquest['flag']) == 0:
        print("Invalid flag for objective " + currentquest['objective'] + ". Valid flags are " + str(aflags[currentquest['objective']]).replace("'","")[1:][:-1])
        print("Skipping to next quest")
        continue
    timesuffix=''
    if currentquest['flag']=='timed':
        timesuffix=' in ' + str(currentquest['time']) + ' seconds'
        questdesc=str(strs[currentquest['objective'] + 't'] + timesuffix + "!")
    elif currentquest['flag']=='endless':
        timesuffix=' until the challenge ends'
        questdesc=str(strs[currentquest['objective'] + 't'] + timesuffix + "!")
    else:
        if currentquest['objective']=='ClasLevel' or currentquest['objective']=='ZenLevel':
            sccond=str(currentquest['condition']+1)
        else:
            sccond=str(currentquest['condition'])
        try:
            if currentquest['timebonus']==1:
                questdesc=str(strs[currentquest['objective']].replace('zxc',sccond) + " as quickly as possible!")
        except:
            questdesc=str(strs[currentquest['objective']].replace('zxc',sccond) + "!")
    if currentquest['objective']=="PokerHand":
        if currentquest['flag']=='value' and currentquest['condition']==1:
                questdesc=questdesc.replace('xbx',str(currentquest['hand']))
        else:
            questdesc=questdesc.replace('xbx',str(currentquest['hand']) + 's')
    print(questdesc)
    waittime=15
    while waittime>0:
        print('You have ' + str(waittime) + ' seconds to get to the gamemode')
        time.sleep(1)
        waittime-=1
    subchallenge(currentquest['objective'])
    i+=1
addscores()