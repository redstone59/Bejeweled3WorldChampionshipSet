from ReadWriteMemory import ReadWriteMemory #install
import json
import psutil #install
from tkinter import filedialog
import os,sys

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

def addscores():
    global finalscore
    finalscore=0
    print('---------------')
    print('Final Score:')
    for x in range (1,i):
        subscript=list(questjson)[x]
        currentquest=questjson[subscript]
        exec("print(currentquest['objective'] +': ' + str(umscore" + str(x) + ") + ' * ' + str(currentquest['multiplier']) + ' = ' + str(score" + str(x) + "))")
        exec("finalscore = finalscore + score" + str(x),globals())
    print("FINAL SCORE : " + str(finalscore))


def subchallenge(id):
    global score
    score=input('type test score: ')
    exec('score' + str(i) + '=int(score)*int(currentquest["multiplier"])',globals())
    exec('umscore' + str(i) + '=int(score)',globals())

#checkGameOpen()
openchal()
strs=json.load(open(p + '\\jsons\\strings.json'))
aflags=json.load(open(p + '\\jsons\\allowedflags.json'))
i=0
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
        try:
            if currentquest['timebonus']==1:
                questdesc=str(strs[currentquest['objective']].replace('zxc',str(currentquest['condition'])) + " as quickly as possible!")
        except:
            questdesc=str(strs[currentquest['objective']].replace('zxc',str(currentquest['condition'])) + "!")
    if currentquest['objective']=="PokerHand":
        if currentquest['flag']=='value' and currentquest['condition']==1:
                questdesc=questdesc.replace('xbx',str(currentquest['hand']))
        else:
            questdesc=questdesc.replace('xbx',str(currentquest['hand']) + 's')
    print(questdesc)
    subchallenge(currentquest['objective'])
    i=i+1
addscores()