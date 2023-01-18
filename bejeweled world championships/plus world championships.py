from ReadWriteMemory import ReadWriteMemory #install
import json
import psutil #install
from tkinter import filedialog
import os,sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pyglet import font
import hashlib
from webbrowser import open as webopen

p = os.path.dirname(os.path.abspath(sys.argv[0])) #default path is the path the file is in (./)
questjson={}

def openchal():
    filetypes=(('JSON file', '*.json'),('All Files','*.*'))
    questpath=filedialog.askopenfilename(title="Open the challenge file",initialdir=p,filetypes=filetypes)
    global questjson
    questjson = json.load(open(questpath))
    try:
        if 'challengeinfo' not in questjson.keys():
            print('Invalid json file')
            openchal()
    except:
        print('Invalid json file')
        openchal()
    print(questjson['challengeinfo']['name'] + " by " + questjson['challengeinfo']['author'] + ".")
    canvas.create_text([(179,35),(233,44),(399,69)][res.get()],text=questjson['challengeinfo']['name'],font=("Flare Gothic",[8,10,14][res.get()]),anchor=tk.CENTER,fill='#ffffff')
    canvas.create_text([(179,51),(233,67),(399,104)][res.get()],text=questjson['challengeinfo']['author'],font=("Flare Gothic",[8,10,14][res.get()]),anchor=tk.CENTER,fill='#ffffff')
    canvas.create_text([(121,66),(155,85),(243,133)][res.get()],text=insert_newlines(questjson['challengeinfo']['description'],30),font=("Flare Gothic",[8,10,14][res.get()]),anchor=tk.NW,fill='#ffffff')
    print(questjson['challengeinfo']['description'])
    if questjson['challengeinfo']['type']=='timed':
        print(str(questjson['challengeinfo']['time']) + 's timed challenge, ' + str(len(questjson)-1) + ' sub-challenges long.')
    else:
        print('Marathon challenge, '+ str(len(questjson)-1) + ' sub-challenges long.')
        print('')
    print(sha256sum(questpath))
    canvas.create_text([(150,470),(196,601),(300,940)][res.get()],text='Challenge hash:\n' + sha256sum(questpath),font=("Flare Gothic",[5,7,10][res.get()]),anchor=tk.CENTER,fill='#ffffff')
    return

def insert_newlines(string, every): #thank you gurney alex (https://stackoverflow.com/questions/2657693/insert-a-newline-character-every-64-characters-using-python)
    return '-\n'.join(string[i:i+every] for i in range(0, len(string), every))

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

def TwosComp32(n): #thank you tim from StackOverflow (why am i an idiot and forgot the link to this one)
    return n - 0x100000000 if n & 0x80000000 else n

def sha256sum(filename): #thank you maxschlepzig for this (https://stackoverflow.com/questions/22058048/hashing-a-file-in-python)
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

def checkGameOpen():
    pluspidlist = findProcessIdByName('popcapgame1.exe')
    if len(pluspidlist) == 0:
        if messagebox.askyesno("Game not found","Bejeweled 3 not found, hit Yes to try again"):
            challenge()
        else:
            return False
    else:
        print('Bejeweled 3 found!')
        global game,addr
        game=ReadWriteMemory().get_process_by_name('popcapgame1.exe')
        game.open()
        addr = game.read(0x400000+0x00487f34)
        return True


def addscores():
    global finalscore
    finalscore=0
    print('---------------')
    print('Final Score:')
    for x in range (1,i):
        subscript=list(questjson)[x]
        currentquest=questjson[subscript]
        print(currentquest['objective'] + ' : ' + f"{umscores[x-1]:,}" + ' * ' + f"{currentquest['multiplier']:,}" + ' = ' + f"{mscores[x-1]:,}")
        canvas.create_text([(262,130*(x-1)),(336,167+46*(x-1)),(526,261+72*(x-1))][res.get()],text='x' + f"{currentquest['multiplier']:,}",font=("Flare Gothic",[12,15,24][res.get()]),anchor=tk.SE,fill='#ffff60')
        canvas.create_text([(262,148*(x-1)),(336,190+46*(x-1)),(526,297+72*(x-1))][res.get()],text=f"{mscores[x-1]:,}",font=("Flare Gothic",[12,15,24][res.get()]),anchor=tk.SE,fill='#ffff60')
        finalscore=finalscore + mscores[x-1]
    print("FINAL SCORE : " + f"{finalscore:,}")
    canvas.create_text([(150,552),(196,707),(300,1105)][res.get()],text=f"{finalscore:,}",font=("Myriad Pro",[24,36,48][res.get()]),anchor=tk.CENTER,fill='#ffffff')
    if timeshow.get()==1 and questjson['challengeinfo']['type']=='timed': canvas.create_text([(150,592),(196,758),(300,1185)][res.get()],text='Timer is shown.',font=("Flare Gothic",[8,10,16][res.get()]),anchor=tk.CENTER,fill='#ffffff')

def hasScoreDecreased():
    global scorelastpass,score,highestscore,sclastpass,subchalfailed
    if game.read(scorepointer) < scorelastpass:
        print('Continuing to the next quest because the score has decreased (reset or game over)')
        score=scorelastpass
        subchalfailed=' (incomplete)'
        return True
    if game.read(scpointer)+condoffset > sclastpass:
        highestscore=game.read(scpointer)+condoffset
    scorelastpass=game.read(scorepointer)
    sclastpass=game.read(scpointer)+condoffset

def isTimeUp():
    if time.time() >= endtime and endtime != 0 and questjson['challengeinfo']['type'] == 'timed': #check if time is up
        global score
        score=scorepointer
        return True
    if questjson['challengeinfo']['type'] == 'timed' and timeshow.get() == 1:
        if divmod(int(endtime - time.time()),60)[1] >= 10: timerlbl['text']=str(divmod(int(endtime - time.time()),60)[0])+':'+str(divmod(int(endtime - time.time()),60)[1])
        else: timerlbl['text']=str(divmod(int(endtime - time.time()),60)[0])+':0'+str(divmod(int(endtime - time.time()),60)[1])
    elif questjson['challengeinfo']['type'] != 'timed' and timeshow.get() == 1:
        timerlbl['text']='Marathon'

def checksubchal():
    global score,iscomplete,condoffset
    iscomplete,score,condoffset=0,0,0
    #gem-based quests
    if currentquest['objective'] in ["Avalanche"]: #still need to find GemGoal
        if currentquest['flag'] == 'value':
            game.write(game.read(addr+0xBE0)+0xE00,goals[str(game.read(game.read(addr+0xBE0)+0x322C))]-currentquest['condition']) #progression of quest is decided by the difference of the condition and the goal of the current quest
            condoffset=goals[str(game.read(game.read(addr+0xBE0)+0x322C))]-currentquest['condition']
        else:
            game.write(game.read(addr+0xBE0)+0xE00,-1000)
    #bomb quests
    if currentquest['objective'] in ["TimeBomb","MatchBomb"]: #still need to find bomb goal (might even be the same as GemGoal)
        game.write(game.read(addr+0xBE0)+0xE00,-1000)
        condoffset=-1000
    #gold rush quests
    #time-based quests
    if currentquest['objective'] in ["BuriedTreasure","GoldRush","Sandstorm","WallBlast"]:
        game.write(game.read(addr+0xBE0)+0x3238,1800) #change quest base time to 30 minutes
    #poker quests
    if currentquest['objective'] in ["Poker","PokerLimit","PokerHand","PokerSkull"]:
        if game.read(game.read(addr+0xBE0)+0x323C) >= 1000: #check if miniquest id is not the one of the secret poker mode
            game.write(game.read(addr+0xBE0)+0x3958,100000) #change PokerGoal to an absurdly high number
            game.write(game.read(addr+0xBE0)+0x395C,1000) #change amount of hands remaining
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
        game.write(game.read(addr+0xBE0)+0xE00,-1000)
        while iscomplete==0:
            if game.read(movepointer)<=0:
                score=TwosComp32(game.read(scpointer))+1000
                iscomplete=1
                return
    if currentquest['flag']=='value':
        if 'timebonus' in currentquest.keys():
            timescore=int(currentquest['time'])*1000
            while iscomplete==0:
                if TwosComp32(game.read(scpointer))>=currentquest['condition']+condoffset or isTimeUp():
                    score=timescore
                    iscomplete=1
                if timescore>=1:
                    time.sleep(0.001)
                    timescore-=1
                gui.update()
                game.write(scorepointer,timescore)

        else:
            while iscomplete==0:
                if TwosComp32(game.read(scpointer))>=currentquest['condition']+condoffset:
                    score=game.read(scorepointer)
                    iscomplete=1
                if hasScoreDecreased() or isTimeUp():
                    iscomplete=1
                    break
                gui.update()
    if currentquest['flag']=='timed':
        scendtime=time.time()+int(currentquest['time'])
        while time.time() <= scendtime:
            if hasScoreDecreased() or isTimeUp():
                    iscomplete=1
                    break
            gui.update()
        score=game.read(scorepointer)
        iscomplete=1
    elif currentquest['flag']=='endless':
        while iscomplete==0:
            if hasScoreDecreased() or isTimeUp():
                    iscomplete=1
                    break
            gui.update()
        score=game.read(scorepointer)

def subchallenge(id):
    global game,scorelastpass,highestscore,scpointer,scorepointer,condoffset,subchalfailed
    del scorelastpass, highestscore, scorepointer, condoffset, subchalfailed
    subchalfailed=''
    game.open()
    scoffset=offset[id] #find offsets for pointer
    if currentquest['objective'] == 'PokerHand':
        handlist=['Pair','Spectrum','Two Pair','3 of a Kind','Full House','4 of a Kind','Flush']
        scoffset[1]=int(scoffset[1],base=16)
        print(str(int(scoffset[1])))
        scoffset[1]=str(int(scoffset[1])+(4*handlist.index(currentquest['hand'])))
        scoffset[1]=str(hex(int(scoffset[1])))
    scpointer=game.read(addr+int(scoffset[0],base=16))
    for m in range (1,len(scoffset)):
        scpointer=scpointer+int(scoffset[m],base=16)
    if mode[currentquest['objective']] == "Diamond Mine": #or mode[currentquest['objective']] == "Quest":
        scorepointer=game.read(addr+0xBE0)+0xE00
    else:
        scorepointer=game.read(addr+0xBE0)+0xD20
    game.write(game.read(addr+0xBE0)+0xD20,0)
    game.write(game.read(addr+0xBE0)+0xE00,0)
    game.write(scpointer,0)
    print('GO!')
    scorelastpass=game.read(scorepointer)
    highestscore=game.read(scorepointer)
    checksubchal()
    #score stuffs
    del scoffset
    mscores.append(int(score)*int(currentquest['multiplier']))
    umscores.append(int(score))
    canvas.create_text([(38,148*(i-1)),(49,190+46*(i-1)),(76,297+72*(i-1))][res.get()],text=f'{int(score):,}' + subchalfailed,font=("Flare Gothic",[12,15,24][res.get()]),anchor=tk.SW,fill='#f4f4d0')
    game.close()

def challenge():
    changeRes()
    if checkGameOpen():
        openchal()
        sm_file.entryconfig("Resolution",state='disabled')
        sm_file.entryconfig("Open",state='disabled')
        sm_chal.entryconfig("Abort",state='active')
        sm_chal.entryconfig("Open",state='disabled')
        sm_chal.entryconfig("Show time left",state='disabled')
        global offset,strs,aflags,mode,mqids,goals,mscores,umscores,i,endtime,scorelastpass,highestscore,scpointer,scorepointer,sclastpass,condoffset,currentquest,isAborted,inChallenge,subchalfailed
        offset=json.load(open(p + '\\jsons\\offsets.json'))
        strs=json.load(open(p + '\\jsons\\strings.json'))
        aflags=json.load(open(p + '\\jsons\\allowedflags.json'))
        mode=json.load(open(p + '\\jsons\\mode.json'))
        mqids=json.load(open(p + '\\jsons\\miniquestids.json'))
        goals=json.load(open(p + '\\jsons\\goals.json'))
        guistrings=json.load(open(p + '\\jsons\\guistrings.json'))
        mscores,umscores=[],[]
        i,endtime,scorelastpass,highestscore,scpointer,scorepointer,sclastpass,condoffset,subchalfailed=0,0,0,0,0,0,0,0,''
        inChallenge=True
        isAborted=False
        for x in questjson:
            currentquest=questjson[x]
            canvas.delete('desc')
            if isAborted == True:
                break
            if time.time() >= endtime and endtime != 0 and questjson['challengeinfo']['flag'] == 'timed': #check if time is up
                print("TIME!")
                break
            if x=='challengeinfo': #print challenge metadata
                if currentquest['type']=='timed': endtime=time.time()+(currentquest['time'])
                else: endtime=time.time()+315576000
                i+=1
                continue
            if aflags[currentquest['objective']].count(currentquest['flag']) == 0:
                print("Invalid flag for objective " + currentquest['objective'] + ". Valid flags are " + str(aflags[currentquest['objective']]).replace("'","")[1:][:-1])
                print("Skipping to next quest")
                continue
            timesuffix=''
            guistring=[]
            guistring.insert(0,guistrings[currentquest['objective']][0])
            if currentquest['flag']=='timed':
                timesuffix=' in ' + str(currentquest['time']) + ' seconds'
                questdesc=str(strs[currentquest['objective'] + 't'] + timesuffix + "!")
                guistring.insert(1,guistrings[currentquest['objective'] + 't'][1])
                guistring.insert(2,'('+str(currentquest['time'])+'s)')
            elif currentquest['flag']=='endless':
                timesuffix=' until the challenge ends'
                questdesc=str(strs[currentquest['objective'] + 't'] + timesuffix + "!")
                guistring.insert(1,guistrings[currentquest['objective']+ 't'][1])
                guistring.insert(2,'(Endless)')
            else:
                if currentquest['objective']=='ClasLevel' or currentquest['objective']=='ZenLevel':
                    sccond=str(currentquest['condition']+1)
                else:
                    sccond=str(currentquest['condition'])
                try:
                    if currentquest['timebonus']==1:
                        questdesc=str(strs[currentquest['objective']].replace('zxc',sccond) + " as quickly as possible!")
                        guistring.insert(1,guistrings[currentquest['objective']][1].replace('zxc',sccond))
                        guistring.insert(2,'('+str(currentquest['time'])+'s)')
                except:
                    questdesc=str(strs[currentquest['objective']].replace('zxc',sccond) + "!")
                    guistring.insert(1,guistrings[currentquest['objective']][1].replace('zxc',sccond))
            if currentquest['objective']=="PokerHand":
                if currentquest['flag']=='value' and currentquest['condition']==1:
                        questdesc=questdesc.replace('xbx',str(currentquest['hand']))
                        guistring[1]=guistring[1].replace('xbx',str(currentquest['hand']))
                else:
                    questdesc=questdesc.replace('xbx',str(currentquest['hand']) + 's')
                    guistring[1]=guistring[1].replace('xbx',str(currentquest['hand']) + 's')
            canvas.create_text([(150,592),(196,758),(300,1185)][res.get()],text=questdesc,font=("Flare Gothic",[8,10,16][res.get()]),anchor=tk.CENTER,fill='#ffffff',tags=('desc'))
            if 'qextra' in currentquest.keys():
                guistring.append('[' + str(currentquest['qextra']) + ']')
            canvas.create_text([(38,130*(i-1)),(49,167+46*(i-1)),(76,261+72*(i-1))][res.get()],text=''.join(guistring),font=("Flare Gothic",[12,15,24][res.get()]),anchor=tk.SW,fill='#f4f4d0')
            if currentquest['objective'] in ["QuestCompleted","DiamondDepth","DiamondTreasure"]: #check for unimplemented sub challenges
                print('oops this one isnt actually implemented yet teehee')
                mscores.append(0)
                umscores.append(0)
                continue
            waittime=10
            endtime+=waittime
            gracetime=time.time()+waittime
            gracepb.place(x=223,y=0)
            if timeshow.get() == 1 and questjson['challengeinfo']['type'] == 'timed':
                timerlbl.place_forget()
            while time.time() < gracetime and isAborted == False:
                gracepb['value']=gracetime-time.time()
                gui.update()
            if isAborted == True:
                break
            gracepb.place_forget()
            if timeshow.get() == 1 and questjson['challengeinfo']['type'] == 'timed':
                timerlbl.place(x=[300,384,600][res.get()],y=11,anchor=tk.E)
            subchallenge(currentquest['objective'])
            i+=1
        canvas.delete('desc')
        addscores()
        inChallenge=False
        sm_file.entryconfig("Resolution",state='active')
        sm_file.entryconfig("Open",state='active')
        sm_chal.entryconfig("Abort",state='disabled')
        sm_chal.entryconfig("Open",state='active')
        sm_chal.entryconfig("Show time left",state='active')
        
isAborted=False
inChallenge=False

def abort():
    global isAborted,iscomplete
    isAborted=True
    iscomplete=1

# tkinter related functions

def changeRes():
    global bgimg,canvas,gracepb
    reslist=['300x620','384x788','600x1220']
    bglist=['normalbg.png','highbg.png','ultrabg.png']
    gui.geometry(reslist[res.get()])
    bgimg = tk.PhotoImage(file=p + '\\images\\' + bglist[res.get()])
    if res.get()==0:
        canvas = tk.Canvas(gui, width=300, height=600, bg='white')
        canvas.place(x=0,y=20)
        bg=canvas.create_image((148,300),image=bgimg)
        canvas.tag_lower(bg)
        gracepb['length']=70
        timerlbl.place(x=300,y=11,anchor=tk.E)
        gui.title('BJ3WC alpha v0.1.1')
    elif res.get()==1:
        canvas = tk.Canvas(gui, width=384, height=768, bg='white')
        canvas.place(x=0,y=20)
        bg=canvas.create_image((190,384),image=bgimg)
        canvas.tag_lower(bg)
        gracepb['length']=154
        timerlbl.place(x=384,y=11,anchor=tk.E)
        gui.title('BJ3WC alpha v0.1.1')
    elif res.get()==2:
        canvas = tk.Canvas(gui, width=600, height=1200, bg='white')
        canvas.place(x=0,y=20)
        bg=canvas.create_image((298,600),image=bgimg)
        canvas.tag_lower(bg)
        gracepb['length']=370
        timerlbl.place(x=600,y=11,anchor=tk.E)
        gui.title('Bejeweled 3 World Championships alpha v0.1.1')
    
def checkchallenge():
    global isAborted
    if inChallenge == True:
        if messagebox.askyesno('Challenge in progress','Are you sure you want to leave mid-challenge?'):
            isAborted=True
            gui.destroy()
            quit()
        else:
            return
    else: 
        gui.destroy()
        quit()

def toggleTime():
    if timeshow.get() == 1:
        timerlbl.place(x=[300,384,600][res.get()],y=11,anchor=tk.E)
    else:
        timerlbl.place_forget()
# tkinter GUI stuffs now

gui=tk.Tk()
gui.iconbitmap(p + '\\g em.ico')
gui.protocol('WM_DELETE_WINDOW',checkchallenge)
gui.geometry('384x788')
gui.title('BJ3WC alpha v0.1.1')
gui.resizable(False,False)

# tk variables
res=tk.IntVar()
res.set(1)
timeshow=tk.IntVar()
timeshow.set(0)
font.add_file(p + "\\fonts\\Flare Gothic Regular.ttf")
font.add_file(p + "\\fonts\\Myriad Pro Regular.ttf")

#menu bar stuffs
sm_file_button=ttk.Menubutton(gui,text='File')
sm_file=tk.Menu(sm_file_button,tearoff=False)
sm_file.add_command(label='Open',underline=0,command=challenge)
ssm_reso=tk.Menu(sm_file,tearoff=False)
ssm_reso.add_radiobutton(label='Normal (300x600)',value=0,variable=res,command=changeRes,state='disabled')
ssm_reso.add_radiobutton(label='High (384x768)',value=1,variable=res,command=changeRes)
ssm_reso.add_radiobutton(label='Ultra (600x1200)',value=2,variable=res,command=changeRes)
sm_file.add_cascade(label='Resolution',menu=ssm_reso)
sm_file.add_command(label='Exit',underline=0,command=checkchallenge)
sm_file_button['menu']=sm_file
sm_chal_button=ttk.Menubutton(gui,text='Challenge')
sm_chal=tk.Menu(sm_chal_button,tearoff=False)
sm_chal.add_command(label='Open',underline=0,command=challenge)
#ssm_pause=sm_chal.add_checkbutton(label='Pause',underline=0,state='disabled')
ssm_abort=sm_chal.add_command(label='Abort',underline=0,state='disabled',command=abort)
ssm_time=sm_chal.add_checkbutton(label='Show time left',underline=0,state='active',variable=timeshow,onvalue=1,offvalue=0,command=toggleTime)
sm_chal_button['menu']=sm_chal
sm_about_button=ttk.Menubutton(gui,text='About')
sm_about=tk.Menu(sm_about_button,tearoff=False)
sm_about.add_command(label='Challenge',underline=0)
sm_about.add_command(label='Documentation',underline=0,command=lambda: webopen('https://docs.google.com/document/d/1RMc6QYoLbh4WKirbTtwDfBR7-BULapBkJrw-ORYdfP8/edit?usp=sharing'))
sm_about.add_command(label='GitHub page',underline=0,command=lambda: webopen('https://github.com/redstone59/Bejeweled3WorldChampionshipSet'))
sm_about_button['menu']=sm_about
sm_file_button.place(x=0,y=0)
sm_chal_button.place(x=60,y=0)
sm_about_button.place(x=150,y=0)

gracepb=ttk.Progressbar(gui,orient='horizontal',mode='determinate',length=154,maximum=10)
timerlbl=ttk.Label(gui,text='0:00',font=("Arial",10))

bgimg = tk.PhotoImage(file=p + '\\images\\highbg.png')

canvas = tk.Canvas(gui, width=300, height=600, bg='white')
canvas.place(x=0,y=20)
canvas.create_image((148,300),image=bgimg)

canvas = tk.Canvas(gui, width=384, height=768, bg='white')
canvas.place(x=0,y=20)
canvas.create_image((190,384),image=bgimg)

gui.mainloop()