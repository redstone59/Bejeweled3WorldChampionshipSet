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
    if currentquest['objective']=='Stratamax':
        print('stratamax')
        movepointer=game.read(addr+0xBE0)+0x323C
        game.write(movepointer,currentquest['condition'])
        while iscomplete==0:
            if game.read(movepointer)<=0:
                score=game.read(scpointer)
                iscomplete=1
                return
    if currentquest['flag']=='value':
        try:
            if currentquest['timebonus']==1:
                print('time bonus val')
                timescore=int(currentquest['time'])*1000
                while iscomplete==0:
                    if game.read(scpointer)>=currentquest['condition']:
                        score=timescore
                        iscomplete=1
                    time.sleep(0.001)
                    if timescore>=1:
                        timescore=timescore-1
        except Exception as e:
            print(e)
            print('non timebonus val')
            while iscomplete==0:
                if game.read(scpointer)>=currentquest['condition']:
                    score=game.read(scpointer)
                    iscomplete=1
    if currentquest['flag']=='timed':
        print('timed chal')
        time.sleep(currentquest['time'])
        score=game.read(scpointer)
        iscomplete=1
    elif currentquest['flag']=='endless':
        print('endless chal')
        input('hit enter to end i havent made a thing that does time yet')
        score=game.read(scpointer)

def subchallenge(id):
    #find pointer
    global game
    game.open()
    scoffset=offset[id]
    global scpointer
    scpointer=game.read(addr+int(scoffset[0],base=16))
    for m in range (1,len(scoffset)):
        scpointer=scpointer+int(scoffset[m],base=16)
    print(hex(scpointer))
    print('GO!')
    checksubchal()
    #score stuffs
    print(score)
    mscores.append(int(score)*int(currentquest['multiplier']))
    umscores.append(int(score))

checkGameOpen()
openchal()
strs=json.load(open(p + '\\jsons\\strings.json'))
aflags=json.load(open(p + '\\jsons\\allowedflags.json'))
offset=json.load(open(p + '\\jsons\\offsets.json'))
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
        i=i+1
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
        waittime=waittime-1
    subchallenge(currentquest['objective'])
    i=i+1
addscores()