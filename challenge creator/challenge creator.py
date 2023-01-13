import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import askyesnocancel
import json
import os,sys

#stupid fuckin path stuff
p = os.path.dirname(os.path.abspath(sys.argv[0]))
olist=json.load(open(p + '\\jsons\\objectivelist.json'))
strs=json.load(open(p + '\\jsons\\strings.json'))
aflags=json.load(open(p + '\\jsons\\allowedflags.json'))

global clen
clen=1
challengeset={"challengeinfo":{},"quest1":{}}
global currentfile
currentfile=""
global savecompare
savecompare={"challengeinfo":{},"quest1":{}}
global saveflag
saveflag=0

def changelen(n):
    global clen
    if n==-1 and clen==1:
        return
    clen=clen+n
    scselector['values']=[str(n+1) for n in range (0, clen)]
    scselector.set(int(scselector.get().split()[0])+n)
    if n==-1 and int(scselector.get().split()[0])==0:
        scselector.set('1')
    if clen+1 > len(challengeset):
        resetwidgets()
    updatesc(1)

def updatedesctext():
    if aflags[scobjective.get()].count(scflag.get().lower()) == 0:
        desctext['text']="Invalid flag for objective " + scobjective.get() + ". Valid flags are " + str(aflags[scobjective.get()]).replace("'","")[1:][:-1]
        return
    timesuffix=''
    if scflag.get().lower()=='timed':
        timesuffix=' in ' + str(int(sctime.get())) + ' seconds'
        desctext['text']=str(strs[scobjective.get() + 't'] + timesuffix + "!")
    elif scflag.get().lower()=='endless':
        timesuffix=' until the challenge ends'
        desctext['text']=str(strs[scobjective.get() + 't'] + timesuffix + "!")
    elif timebon.get()=='1':
        desctext['text']=str(strs[scobjective.get()].replace('zxc',str(sccondition.get())) + " as quickly as possible!")
    else:
        desctext['text']=str(strs[scobjective.get()].replace('zxc',str(sccondition.get())) + "!")
    if scobjective.get()=="PokerHand":
        if int(sccondition.get())==1 and scflag.get().lower()=='value':
            desctext['text']=desctext.cget('text').replace('xbx',str(schand.get()))
        else:
            desctext['text']=desctext.cget('text').replace('xbx',str(schand.get()) + 's')
    scselector['values']=[str(n+1)+' - '+challengeset['quest'+str(n+1)]['objective'] for n in range (0, clen)]
    savesubchal(int(scselector.get().split()[0]))
        

def updateflags(n):
    sccondition.grid_forget()
    sctimebonus.grid_forget()
    sctime.grid_forget()
    timlbl.grid_forget()
    conlbl.grid_forget()
    tmblbl.grid_forget()
    timebon.set("0")
    if scflag.get() == "Timed":
        sctime.grid(column=3,row=11)
        timlbl.grid(column=2,row=11,pady=2)
    elif scflag.get() == "Value":
        sccondition.grid(column=3,row=9)
        sctimebonus.grid(column=3,row=10)
        conlbl.grid(column=2,row=9,pady=2)
        tmblbl.grid(column=2,row=10,pady=2)
    else:
        updatedesctext()
    if scobjective.get()=="PokerHand":
        hanlbl.grid(column=2,row=12)
        schand.grid(column=3,row=12,pady=5)
    if scobjective.get() in ["Avalanche","Butterflies","ButterClear","ButterCombo","TimeBomb","MatchBomb"]:
        if scobjective.get() =="Avalanche":
            extlbl['text']='# gems/move'
        if scobjective.get() in ['Butterflies','ButterClear','ButterCombo']:
            extlbl['text']='# matches/move'
        if scobjective.get() in ['TimeBomb','MatchBomb']:
            extlbl['text']='Start bomb #'
        extlbl.grid(column=2,row=13)
        scext.grid(column=3,row=13)

def resetwidgets():
    sccondition.grid_forget()
    sctimebonus.grid_forget()
    sctime.grid_forget()
    timlbl.grid_forget()
    conlbl.grid_forget()
    tmblbl.grid_forget()
    scext.grid_forget()
    extlbl.grid_forget()
    timebon.set("0")
    scobjective.set("Cascade")
    scflag.set("")
    mulbox.set(1)
    sccondition.insert(0,"")
    scflag.set("")
    schand.set("")
    desctext['text']='Sub-challenge text will appear here'

def timebonusenable():
    if timebon.get()=='1':
        sctime.grid(column=3,row=11)
        timlbl.grid(column=2,row=11,pady=2)
    else:
        sctime.grid_forget()
        timlbl.grid_forget()
    updatedesctext()

def updatesc(n):
    if len(challengeset)-1>=int(scselector.get().split()[0]):
        loadset=challengeset["quest" + scselector.get().split()[0]]
        scobjective.set(loadset['objective'])
        scflag.set(str(loadset['flag']).capitalize())
        mulbox.set(loadset['multiplier'])
        updateflags(1)
        if 'condition' in loadset.keys():
            sccondition.delete(0,len(sccondition.get()))
            sccondition.insert(0,str(loadset['condition']))
        if 'time' in loadset.keys():
            sctime.delete(0,len(sctime.get()))
            sctime.insert(0,str(int(loadset['time'])))
        if "PokerHand" in loadset.values():
            schand.set(loadset['hand'])
        if 'timebonus' in loadset.keys():
            timebon.set('1')
            timebonusenable()
        if loadset['objective'] in ['Avalanche','Butterflies','ButterClear','ButterCombo','TimeBomb','MatchBomb']:
            scext.delete(0,len(scext.get()))
            scext.insert(0,(str(int(loadset['qextra']))))
        updatedesctext()
    else:
        resetwidgets()


def handcheck(n):
    hanlbl.grid_forget()
    schand.grid_forget()
    extlbl.grid_forget()
    scext.grid_forget()
    if scobjective.get()=="PokerHand":
        hanlbl.grid(column=2,row=12)
        schand.grid(column=3,row=12,pady=5)
    if scobjective.get() in ["Avalanche","Butterflies","ButterClear","ButterCombo","TimeBomb","MatchBomb"]:
        if scobjective.get() =="Avalanche":
            extlbl['text']='# gems/move'
        if scobjective.get() in ['Butterflies','ButterClear','ButterCombo']:
            extlbl['text']='# matches/move'
        if scobjective.get() in ['TimeBomb','MatchBomb']:
            extlbl['text']='Start bomb #'
        extlbl.grid(column=2,row=13)
        scext.grid(column=3,row=13)

def updatetype():
    if timedchallenge.get()=='1':
        ctimelbl.grid(column=2,row=4,pady=5)
        ctime.grid(column=3,row=4)
        scflag['values']=['Timed','Value','Endless']
    else:
        ctimelbl.grid_forget()
        ctime.grid_forget()
        scflag['values']=['Timed','Value']

def saveset(target, set):
    challengeset[target]=set
    global saveflag
    saveflag=0
    if cr.title()[-1:] != '*':
        cr.title(cr.title()+'*')

def saveinfo(n):
    info={}
    info['name']=cname.get()
    info['author']=cauthor.get()
    info['description']=cdesc.get()
    info['type']='marathon'
    if timedchallenge.get()=='1':
        info['type']='timed'
        info['time']=int(ctime.get())
    saveset('challengeinfo',info)

def savesubchal(scn):
    if scn=="" or scflag=="":
        return
    subchal={}
    subchal['objective']=scobjective.get()
    subchal['flag']=scflag.get().lower()
    if scflag.get().lower() == 'timed':
        subchal['time']=int(sctime.get())
    elif scflag.get().lower() == 'value':
        subchal['condition']=int(sccondition.get())
        if timebon.get()=='1':
            subchal['timebonus']=1
            subchal['time']=sctime.get()
    if scobjective.get()=="PokerHand":
        subchal['hand']=schand.get()
    if scobjective.get() in ["Avalanche","Butterflies","ButterClear","ButterCombo","TimeBomb","MatchBomb"]:
        subchal['qextra']=int(scext.get())
    subchal['multiplier']=int(mulbox.get())
    saveset('quest' + str(scn),subchal)

def newfile():
    global challengeset
    global savecompare
    if saveflag==0 and challengeset!=savecompare:
        c=askyesnocancel(title='Unsaved changes',message='Save before creating new file?')
        if c == True:
            savefile()
        elif c == None:
            return
    global clen
    clen=1
    challengeset={"challengeinfo":{},"quest1":{}}
    savecompare={"challengeinfo":{},"quest1":{}}
    global currentfile
    currentfile=""
    scselector['values']=[n+1 for n in range (0, clen)]
    cname.delete(0,len(cname.get()))
    cauthor.delete(0,len(cauthor.get()))
    cdesc.delete(0,len(cdesc.get()))
    timedchallenge.set('0')
    ctime.set("")
    ctime.grid_forget()
    ctimelbl.grid_forget()
    resetwidgets()
    scselector.set('1')

def openfile():
    global saveflag
    global challengeset
    global savecompare
    if saveflag==0 and challengeset!=savecompare:
        c=askyesnocancel(title='Unsaved changes',message='Save before closing?')
        if c == True:
            savefile()
        elif c == None:
            return
    filetypes=(('JSON file', '*.json'),('All Files','*.*'))
    global currentfile
    currentfile=filedialog.askopenfilename(title="Pick a file location",initialdir='./',filetypes=filetypes)
    try:
        challengeset=json.load(open(currentfile))
    except:
        desctext['text']='Failed to open file, try again.'
        return
    if 'challengeinfo' not in challengeset.keys():
        desctext['text']='Invalid json file.'
        return
    savecompare=challengeset
    cr.title("BJ3WC Challenge Creator - " + currentfile)
    saveflag=1
    scselector.set('1'+' - '+challengeset['quest1']['objective'])
    global clen
    clen=len(challengeset)-1
    scselector['values']=[str(n+1)+' - '+challengeset['quest'+str(n+1)]['objective'] for n in range (0, clen)]
    updatesc(1)
    updateflags(1)
    infoset=challengeset['challengeinfo']
    cname.insert(0,str(infoset['name']))
    cauthor.insert(0,infoset['author'])
    cdesc.insert(0,infoset['description'])
    if infoset['type']=='timed':
        timedchallenge.set('1')
        ctime.set(infoset['time'])
    updatetype()

def savefile():
    global currentfile
    if currentfile=="":
        filetypes=(('JSON file', '*.json'),('All Files','*.*'))
        if cname.get()=="":
            currentfile=filedialog.asksaveasfilename(title="Pick a save location",initialdir='./',filetypes=filetypes,initialfile="My Bejeweled 3 Challenge.json")
        else:
            currentfile=filedialog.asksaveasfilename(title="Pick a save location",initialdir='./',filetypes=filetypes,initialfile=cname.get()+".json")
    p=open(currentfile,"w")
    p.write(str(challengeset).replace("'",'"'))
    desctext['text']='Saved file at ' + currentfile
    p.close()
    global savecompare
    savecompare=challengeset
    cr.title("BJ3WC Challenge Creator - " + currentfile)
    global saveflag
    saveflag=1

def checksave():
    if saveflag==0 and challengeset!=savecompare:
        c=askyesnocancel(title='Unsaved changes',message='Save before exiting?')
        if c == True:
            savefile()
        elif c == None:
            return
    cr.destroy()

cr = tk.Tk()
cr.title("BJ3WC Challenge Creator")
cr.protocol('WM_DELETE_WINDOW',checksave)
cr.resizable(False,False)
timedchallenge=tk.StringVar()
timebon=tk.StringVar()
subchaltime=tk.StringVar()

ttk.Button(text="New",command=newfile).grid(column=1,row=0,padx=5,pady=5)
ttk.Button(text="Open",command=openfile).grid(column=1,row=1,padx=5,pady=5)
ttk.Button(text="Save",command=savefile).grid(column=1,row=2,padx=5,pady=5)

#challenge info editor

ttk.Label(text='Name: ').grid(column=2,row=0)
cname=ttk.Entry(cr,width=45)
cname.grid(column=3,row=0,columnspan=4)
cname.bind('<KeyRelease>',saveinfo)

ttk.Label(text='Author: ').grid(column=2,row=1)
cauthor=ttk.Entry(cr,width=45)
cauthor.grid(column=3,row=1,columnspan=4)
cauthor.bind('<KeyRelease>',saveinfo)

ttk.Label(text='Description: ').grid(column=2,row=2)
cdesc=ttk.Entry(cr,width=45)
cdesc.grid(column=3,row=2,columnspan=4)
cdesc.bind('<KeyRelease>',saveinfo)

ttk.Label(text='Timed challenge? ').grid(column=2,row=3,pady=5)
ctype=ttk.Checkbutton(cr,variable=timedchallenge,onvalue='1',offvalue='0',command=updatetype)
ctype.grid(column=3,row=3)

ctimelbl=ttk.Label(text='Time: ')
ctime=ttk.Spinbox(cr,from_=1,to=86400)
ctime.bind('<KeyRelease>',saveinfo)

ttk.Separator(cr,orient='horizontal').grid(column=1,row=5,columnspan=5,sticky='ew',pady=10)


#subchallenge creation

ttk.Label(text='Subchallenge #: ').grid(column=2,row=6,pady=2)
scselector = ttk.Combobox(cr,state='readonly')
scselector['values']=[n+1 for n in range (0, clen)]
scselector.set('1')
scselector.bind('<<ComboboxSelected>>',updatesc)
scselector.bind('<FocusIn>',lambda a:savesubchal(int(scselector.get().split()[0])), add='+')
scselector.grid(column=3,row=6,padx=5)
ttk.Button(text="Add sub-challenge to end",command=lambda:changelen(1)).grid(column=4,row=6)
ttk.Button(text="Remove end sub-challenge",command=lambda:changelen(-1)).grid(column=4,row=7,padx=5)

ttk.Label(text="Objective: ").grid(column=2,row=7,pady=2)
scobjective = ttk.Combobox(cr)
scobjective['values']=[x for x in olist]
scobjective.set('Cascade')
scobjective.grid(column=3,row=7)
scobjective.bind("<<ComboboxSelected>>",handcheck)

ttk.Label(text='Flag: ').grid(column=2,row=8,pady=2)
scflag = ttk.Combobox(cr)
scflag['values']=['Timed','Value']
scflag.bind('<<ComboboxSelected>>',updateflags)
scflag.grid(column=3,row=8)

conlbl=ttk.Label(text='Condition: ')
sccondition = ttk.Entry(cr)
sccondition.bind("<KeyRelease>",lambda a:updatedesctext())

tmblbl=ttk.Label(text='Score with time? ')
sctimebonus = ttk.Checkbutton(cr,variable=timebon,onvalue='1',offvalue='0',command=timebonusenable)

timlbl=ttk.Label(text='Time: ')
sctime = ttk.Entry(cr,textvariable=subchaltime)
sctime.bind("<KeyRelease>",lambda a:updatedesctext())

hanlbl=ttk.Label(text='Poker Hand')
schand = ttk.Combobox(cr)
schand['values']=['Pair','Spectrum','Two Pair','3 of a Kind','Full House','4 of a Kind','Flush']
schand.bind('<<ComboboxSelected>>',lambda a:updatedesctext())

extlbl=ttk.Label(text='Quest Extra')
scext=ttk.Entry(cr)
scext.bind('<<ComboboxSelected>>',lambda a:updatedesctext())

ttk.Label(cr,text='Multiplier: ').grid(column=2,row=14,pady=2)
mulbox = ttk.Spinbox(cr,from_=1,to=999)
mulbox.set(1)
mulbox.bind("<Enter>",lambda a:savesubchal(scselector.get().split()[0]))
mulbox.grid(column=3,row=14)

desctext=ttk.Label(cr)
desctext['text']='Sub-challenge text will appear here'
desctext.grid(column=1,row=15,columnspan=5,pady=5)

cr.mainloop()