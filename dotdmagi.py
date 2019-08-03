''' Best Magic Calculator for Dawn of the Dragons
    usage: dotdmagi.py numsspellslots tag1 [tag2 [tag3...]]
    returns: Details of best magics from best to worst and a short string to
             paste on raids regarding which magics should be used
'''

import sys,os,copy,math
try:
    SLOTNUM = int(sys.argv[1])
    EXTRAFUNC = ''
except:
    SLOTNUM = 0
    EXTRAFUNC = sys.argv[1]
SHOWDEBUG = False
USERAREMAGIC = False
RAIDTAGS = sys.argv[2:]
MAGICLIST = []

OWNED = {
    'MOUNTS':400,
    'LEGIONS':100,
    'MAGICS':30,
    'SPELLS':['TotH',"IS","FS"],
    'GIANTESSENCE':1,
    'BEASTMANESSENCE':18,
    'FESTIVALESSENCE':6,
    'UNDERGROUNDESSENCE':15,
    'DWARFTROOPS':44,
    'DWARFGENERALS':18,
    'MAGICALBEINGTROOPS':10,
    'MAGICALBEINGGENERALS':10,
    'DRAGONESSENCE':10,
    'DRAGONMOUNTS':20,
    "KATH'IN":False,   #For Fury of the Deep, since owning this gen affects it greatly.
    
}
if EXTRAFUNC == 'showparams':
    print "Showing internal parameters of magic calc, dict: OWNED"
    for i in OWNED:
        print str(i)+": "+str(OWNED[i])
    sys.exit()


''' Class documentation: Magic()
    Uses a reverse-creation scheme.
    0.  Instantiate a Magic() class with fullname and nickname. All the really
        important stuff is stored in class variables so any instance you make
        doesn't need to persist past setting up that particular magic.
    1.  Define triggers for a proc. All triggers per damage proc must match
        before damage for that proc is processed
    2.  Define damage for previously defined triggers. Doing this flushes the
        trigger table and primes class to accept new triggers for a new damage.
        This may be a lambda function in case damage is based on trigger params
        Unconditional damage is done without defining new triggers.
    3.  Define proc chance. This ties in all previously defined damage triggers
        and flushes the damage and trigger tables. At this point, most magics
        are complete in definition.
    Supported triggers:
    'raidtag':  Matches against supplied input tags. More than one tag per
                trigger indicates an OR situation where any one tag may match.
    'spellcast':    Matches against whether or not a spell is previously cast.
                    This allows an optimiation via iteration of magic assembly.
    'spellowned':   Matches against spells in the ownership static list

'''



class Magic(object):
    spelllist = []
    magic_id = 1
    def __init__(self,fullname,nickname):
        self.proclist = []  #list of 2-lists of [procrate,[listofprocs]]
        self.curproc = list()   #proc entry [procDamage, {triggercond:triggerdata,...}]
        self.temptrigger = dict()
        self.fullname = fullname
        self.nickname = nickname
        self.israre = False
        
        self.id = Magic.magic_id
        Magic.magic_id += 1
        Magic.spelllist.append(self)
        
    def newTrig(self,triggertype,triggerdata):
        if not isinstance(triggerdata,(list,tuple)):
            triggerdata = [triggerdata]
        self.temptrigger[triggertype] = triggerdata
    def newTrigTag(self,triggerdata):
        self.newTrig('raidtag',triggerdata)
    def newDmg(self,procdamage):
        self.curproc.append([procdamage,copy.deepcopy(self.temptrigger)])
        self.temptrigger = dict()
    def newProc(self,procrate):
        self.proclist.append([procrate,copy.deepcopy(self.curproc)])
        self.curproc = list()
    def setRare(self):
        self.israre = True
    def setrare(self): self.setRare() #convenience
        
    @classmethod
    def getSpell(cls,spellid):
        for i in cls.spelllist:
            if i.id == spellid:
                return i
        return cls.spelllist[0]
        
    @staticmethod
    def getID(name_or_nick):
        for spell in Magic.spelllist:
            if name_or_nick == spell.fullname or name_or_nick == spell.nickname:
                return spell.id
        return 0
        
    def getAvg(self):
        global RAIDTAGS,MAGICLIST,OWNED,USERAREMAGIC,SHOWDEBUG
        curproctotal = 0
        if self.israre and not USERAREMAGIC:
            return 0
        #print "Proclist: "+str(self.proclist)
        for procs in self.proclist:
            procrate = procs[0]
            if SHOWDEBUG: print "procrate: "+str(procrate)+", numprocs in this rate: "+str(len(procs[1]))
            for proc in procs[1]:
                procdamage = proc[0]
                triggered = 0
                triggers = proc[1]
                if SHOWDEBUG: print "procdamage: "+str(procdamage)
                if SHOWDEBUG: print "triggers: "+str(triggers)
                if 'none' in triggers:
                    triggered += 1
                if 'raidtag' in triggers:
                    for tag in RAIDTAGS:
                        if tag in triggers['raidtag']:
                            triggered += 1
                            break
                if 'spellcast' in triggers:
                    for magic in MAGICLIST:
                        magic = magic[0]  #First entry is actual spell
                        data = triggers['spellcast']
                        #convert spell names into IDs to membership test against
                        for i in range(len(data)):
                            if isinstance(data[i],str):
                                data[i] = self.getID(data[i])
                        if magic.id in data:
                            triggered += 1
                            break
                if 'spellowned' in triggers:
                    for magic in OWNED['SPELLS']:
                        id = self.getID(magic)
                        data = triggers['spellowned']
                        #convert spell names into IDs to membership test against
                        for i in range(len(data)):
                            if isinstance(data[i],str):
                                data[i] = self.getID(data[i])
                        if id in data:
                            triggered += 1
                            break
                #
                #add in other trigger conditions
                #
                if triggered == len(triggers):
                    if SHOWDEBUG: print "Condition true"
                    if callable(procdamage):
                        procdamage = procdamage()
                    curproctotal += round((procdamage * procrate) / 100.0,2)
                else:
                    if SHOWDEBUG: print "Condition false"
        return curproctotal
## ----------------------------- MAGIC DATA ENTRY --------------------------- ##
Magic("NULL_ENTRY","NULL_ENTRY")
#
m = Magic("Traditions of the Hunt","TotH")
m.newTrigTag('beast')
m.newDmg(300)
m.newTrig('spellowned','TotH')
m.newTrigTag('beast')
m.newDmg(250)
m.newDmg(250)  #unconditional
m.newProc(15)
#
m = Magic("Mark of the Infinite Dawn","MID")
#   This magic define does not account for infinite dawn set ownership.
#   Any increase in this case will be negligible.
m.newDmg(1980)
m.newTrigTag('dragon')
m.newDmg(590)
m.newTrigTag('worldraid')
m.newDmg(590)
m.newTrigTag('eventraid')
m.newDmg(590)
m.newTrigTag('elite')
m.newDmg(590)
m.newTrigTag('deadly')
m.newDmg(590)
m.newProc(5)
#
m = Magic("Dark Forest","DF")
m.newDmg(315)
m.newDmg(lambda : 5 * math.floor(OWNED['MOUNTS']/3))
m.newTrigTag('dragon')
m.newTrig('spellcast','MID')
m.newDmg(350)
m.newTrigTag('beast')
m.newTrig('spellcast','TotH')
m.newDmg(350)
m.newProc(10)
#
m = Magic("Typhoon","typh")
m.newDmg(375)
m.newTrigTag('abyssal')
m.newDmg(25)
m.newTrigTag('abyssal')
m.newTrig('spellcast','Electrify')
m.newDmg(25)
m.newTrigTag('terror')
m.newDmg(30)
m.newTrigTag('terror')
m.newTrig('spellcast','Crushing Pressure')
m.newDmg(30)
m.newProc(20)
#
m = Magic("Djinnpocalypse","Dj")
#   This spell wants to know if you own Wish Warriors or Arch Djinn's Lamp.
#   Not going to bother with that at this time, even if the damage could add up
m.newDmg(1000)
m.newTrigTag('magicalcreature')
m.newDmg(150)
m.newProc(10)
#
m = Magic("Eyes in the Dark","EitD")
m.newDmg(300)
m.newTrigTag('shadowelf')
m.newDmg(66)
m.newTrigTag('shadowelf')
m.newTrig('spellcast','A Light in the Darkness')
m.newDmg(26)
m.newProc(30)
#
m = Magic("Blinding Light","BL")
m.newDmg(100)
m.newTrigTag('abyssal')
m.newDmg(500)
m.newTrigTag('terror')
m.newDmg(100)
m.newProc(10)
m.newTrigTag('aquatic')
m.newDmg(300)
m.newProc(12)
#
m = Magic("Ice Storm","IS")
m.newDmg(500)
m.newTrigTag('winter')
m.newDmg(90)
m.newTrigTag('winter')
m.newTrig('spellowned','Ice Storm')
m.newDmg(60)
m.newProc(15)
#
m = Magic("Gravebane","GB")
m.newDmg(100)
m.newTrigTag('undead')
m.newDmg(500)
m.newTrigTag('undead')
m.newTrig('spellowned','Gravebane')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Titan Killer","TK")
m.newDmg(200)
m.newTrigTag('giant')
m.newDmg(1100)
m.newDmg(lambda : 50 * OWNED['GIANTESSENCE'])
m.newProc(6)
#
m = Magic("Bestial Downfall","BD")
m.newDmg(30)
m.newDmg(lambda : 4 * OWNED['BEASTMANESSENCE'])
m.newTrigTag('beastman')
m.newDmg(35)
m.newProc(80)
#
m = Magic("Savage Melodies","SaM")  ## SM changed to SaM to avoid collision with Shattered Moon
m.newTrigTag('giant')
m.newDmg(500)
m.newProc(20)
#
m = Magic("Intermission","int")
m.newDmg(100)
m.newDmg(lambda : 12 * OWNED['FESTIVALESSENCE'])
m.newTrigTag('festival')
m.newDmg(100)
m.newProc(35)
#
m = Magic("Flame Serpent","FS")
m.newDmg(250)
m.newTrig('spellowned',"Flame Serpent")
m.newDmg(200)
m.newProc(15)
#
m = Magic("Annihilate","anni")
m.newDmg(125)
m.newTrigTag('construct')
m.newDmg(300)
m.newTrigTag('construct')
m.newTrig('spellowned','Annihilate')
m.newDmg(200)
m.newProc(13)
m.newDmg(600)
m.newProc(2)
#
m = Magic("Conflagration","conf")
#   Checks for Incinerated Soldiers owned. We aren't doing that here.
m.newTrigTag('winter')
m.newDmg(100)
m.newTrigTag('winter')
m.newTrig('spellowned','Living Flame')
m.newDmg(100)
m.newTrigTag('winter')
m.newTrig('spellcast','Flame Serpent')
m.newDmg(150)
m.newProc(25)
#
m = Magic("What's At Stake","WaS")
m.newDmg(100)
m.newTrigTag('undead')
m.newDmg(250)
m.newTrigTag('dragon')
m.newDmg(250)
m.newProc(20)
#
m = Magic("Shattered Moon","SM")
#   This checks if Ying of the Shattered Moon is owned. We're not doing that.
m.newDmg(200)
m.newTrig('spellowned','Shattered Moon')
m.newDmg(100)
m.newTrigTag('human')
m.newDmg(750)
m.newProc(10)
#
m = Magic("Guzzlebeard's Special Reserve","GSR")
m.newDmg(100)
m.newDmg(lambda : 5 * (OWNED['DWARFTROOPS'] + OWNED['DWARFGENERALS']) )
m.newTrigTag('underground')
m.newDmg(400)
m.newTrig('spellcast','A Light in the Darkness')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Acid Flask","AF")
m.newDmg(100)
m.newTrig('spellowned','Acid Flask')
m.newDmg(150)
m.newTrigTag('elite')
m.newDmg(500)
m.newProc(10)
#
m = Magic("Disintegrate","disi")
m.newDmg(300)
m.newTrig('spellowned','High Seas Enigma')
m.newDmg(200)
m.newTrig('spellowned','Volcanic Enigma')
m.newDmg(200)
m.newTrig('spellowned','Celestial Enigma')
m.newDmg(200)
m.newTrigTag('festival')
m.newDmg(400)
m.newProc(9)
#
m = Magic("High Seas Enigma","HSE")
m.newDmg(150)
m.newTrig('spellowned',"Volcanic Enigma")
m.newDmg(100)
m.newTrigTag('aquatic')
m.newDmg(400)
m.newTrigTag('aquatic')
m.newTrig('spellcast',"Celestial Enigma")
m.newDmg(200)
m.newProc(11)
#
m = Magic("Celestial Enigma","CE")
m.newDmg(150)
m.newTrig('spellowned',"High Seas Enigma")
m.newDmg(100)
m.newTrigTag('deadly')
m.newDmg(400)
m.newTrigTag('deadly')
m.newTrig('spellcast',"Volcanic Enigma")
m.newDmg(200)
m.newProc(11)
#
m = Magic("Volcanic Enigma","VE")
m.newDmg(150)
m.newTrig('spellowned',"Celestial Enigma")
m.newDmg(100)
m.newTrigTag('dragon')
m.newDmg(400)
m.newTrigTag('dragon')
m.newTrig('spellcast',"High Seas Enigma")
m.newDmg(200)
m.newProc(11)
#
m = Magic("Wolpertinger Venom","WV")
m.newDmg(15)
m.newTrig('spellowned',"Death Echo")
m.newDmg(70)
m.newTrig('spellowned',"Deadly Strike")
m.newDmg(70)
m.newTrig('spellowned',"Wolpertinger Venom")
m.newDmg(100)
m.newTrig('spellowned',"Lesser Poison")
m.newDmg(30)
m.newTrig('spellowned',"Poison")
m.newDmg(30)
m.newTrig('spellowned',"Greater Poison")
m.newDmg(30)
m.newTrig('spellowned',"Assassin's Delight")
m.newDmg(30)
m.newTrig('spellowned',"Manticore Venom")
m.newDmg(30)
m.newProc(20)
#
m = Magic("Deadly Strike","DS")
m.newDmg(800)
m.newTrig('spellcast',"Death Echo")
m.newDmg(400)
m.newTrig('spellowned',"Deadly Strike")
m.newDmg(100)
m.newProc(5)
#
m = Magic("Death Echo","DE")
m.newDmg(400)
m.newTrig('spellowned',"Death Echo")
m.newDmg(50)
m.newProc(10)
#
m = Magic("Gag Gift","GG")
m.newDmg(700)
m.newTrig('spellowned',"Gag Gift")
m.newDmg(100)
m.newProc(5)
#
m = Magic("A Light in the Darkness","LitD")
m.newDmg(40)
m.newDmg( lambda : 15 * OWNED['UNDERGROUNDESSENCE'] )
m.newTrigTag('underground')
m.newDmg(600)
m.newProc(7)
#
m = Magic("Guster's Fault","GF")
#   This one is complicated. Did some preprocessing to make it fit our paradigm
m.newDmg(190)
m.newProc(20)
#
m = Magic("Heaven's Kiss","HvK")
m.newDmg(10)
m.newTrig('spellcast',"A Light in the Darkness")
m.newDmg(50)
m.newTrigTag('shadowelf')
m.newDmg(700)
m.newTrigTag('elite')
m.newDmg(600)
m.newProc(12)
#
m = Magic("Lesser Poison","LP")
m.newDmg(2)
m.newProc(4)
#
m = Magic("Poison","P")
m.newDmg(4)
m.newProc(7)
#
m = Magic("Greater Poison","GP")
m.newDmg(8)
m.newProc(15)
#
m = Magic("Assassin's Delight","AD")
m.newDmg(50)
m.newTrig('spellcast',"Lesser Poison")
m.newDmg(50)
m.newTrig('spellcast',"Poison")
m.newDmg(50)
m.newTrig('spellcast',"Greater Poison")
m.newDmg(50)
m.newProc(8)
#
m = Magic("Manticore Venom","MV")
m.newDmg(100)
m.newTrig('spellowned',"Manticore Venom")
m.newDmg(100)
m.newTrig('spellowned',"Fey Flame")
m.newDmg(100)
m.newTrig('spellowned',"Dragon's Breath")
m.newDmg(100)
m.newTrig('spellowned',"Poison")
m.newDmg(25)
m.newTrig('spellowned',"Greate Poison")
m.newDmg(25)
m.newTrig('spellowned',"Lesser Poison")
m.newDmg(25)
m.newTrig('spellowned',"Assassin's Delight")
m.newDmg(25)
m.newTrigTag('beast')
m.newDmg(250)
m.newProc(5)
#
m = Magic("Soul Pilferer","SP")
#   Checks for number of Grave Guardians owned. We don't do this.
m.newTrigTag('undead')
m.newDmg(300)
m.newTrigTag('undead')
m.newTrig('spellcast',"Gravebane")
m.newDmg(400)
m.newProc(15)
#
m = Magic("Blessing of Mathala","BoM")
#   This magic checks for those gauntlet trophies. Not doing that here.
m.setrare()
m.newDmg(850)
m.newTrig('spellowned',"BoM")
m.newDmg(100)
m.newProc(12)
#
m = Magic("SMITE","SMITE")
#   This magic also checks for those gauntlet trophies. Not doing that here.
m.setrare()
m.newDmg(500)
m.newTrig('spellowned',"SMITE")
m.newDmg(150)
m.newProc(22)
#
m = Magic("Veil Dust","VD")
m.newDmg(300)
m.newTrig('spellowned',"Veil Dust")
m.newDmg(50)
m.newTrig('spellowned',"Fey Flame")
m.newDmg(50)
m.newTrigTag('magicalcreature')
m.newDmg(400)
m.newProc(10)
#
m = Magic("Fey Flame","fey")
#   This checks for Kindly Folk set. We're not going to do that.
m.newDmg(25)
m.newDmg( lambda : OWNED['MAGICALBEINGTROOPS'] + OWNED['MAGICALBEINGGENERALS'] )
m.newTrig('spellowned',"Fey Flame")
m.newDmg(25)
m.newTrig('spellowned',"Dragon's Breath")
m.newDmg(25)
m.newTrig('spellowned',"Manticore Venom")
m.newDmg(25)
m.newTrigTag('human')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Dragon's Breath","DB")
m.newDmg(25)
m.newDmg( lambda : 5 * (OWNED['DRAGONESSENCE'] + OWNED['DRAGONMOUNTS']) )
m.newTrig('spellowned',"Dragon's Breath")
m.newDmg(25)
m.newTrig('spellowned',"Fey Flame")
m.newDmg(25)
m.newTrig('spellowned',"Manticore Venom")
m.newDmg(25)
m.newProc(10)
#
m = Magic("Visions of the Deep","VotD")
#   This counts Depth Terror set. We're not doing that.
m.newDmg(500)
m.newTrigTag(['terror','abyssal']) #OR condition. Apply proc once.
m.newDmg(58)
m.newTrigTag('terror')
m.newTrig('spellcast',"Typhoon")
m.newDmg(28)
m.newProc(20)
#
m = Magic("Putrid Swamp","PS")
m.newDmg(825)
m.newTrigTag(['orc','ogre','goblin']) #OR CONDITION
m.newTrig('spellcast',"Pestilent Bolt")
m.newDmg(125)
m.newTrigTag('dragon')
m.newTrig('spellcast',"Contagion")
m.newDmg(125)
m.newTrigTag(['human','beastman']) #OR CONDITION
m.newTrig('spellcast',"Noxious Breath")
m.newDmg(125)
m.newProc(10)
#
m = Magic("Pestilent Bolt","PB")
m.newDmg(550)
m.newTrigTag(['orc','ogre','goblin']) #OR CONDITION
m.newTrig('spellcast',"Pestilent Bolt")
m.newDmg(170)
m.newProc(15)
#
m = Magic("Contagion","cont")
m.newDmg(1650)
m.newTrigTag('dragon')
m.newDmg(510)
m.newProc(5)
#
m = Magic("Noxious Breath","NB")
m.newDmg(400)
m.newTrigTag(['human','beastman']) #OR CONDITION
m.newDmg(140)
m.newProc(20)
#
m = Magic("Electrify","elec")
m.newDmg(75)
m.newTrigTag('abyssal')
m.newDmg(200)
m.newTrigTag('insect')
m.newDmg(350)
m.newProc(10)
#
m = Magic("Crushing Pressure","CP")
m.newDmg(50)
m.newTrig('spellcast','Boil')
m.newDmg(20)
m.newTrig('spellcast','Feeding Frenzy')
m.newDmg(20)
m.newTrig('spellcast','Deep Freeze')
m.newDmg(20)
m.newTrigTag('aquatic')
m.newDmg(50)
m.newTrigTag('terror')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Boil","boil")
#   Checks if five particular generals are owned. No way we're doing that.
m.newDmg(50)
m.newTrigTag('aquatic')
m.newDmg(250)
m.newProc(11)
#
m = Magic("Feeding Frenzy","FF")
#   Checks for ownership of Monster Fisherman and Fish Hooks. Not doing that.
#   Since its damage is so significant, we'll do the cheap way out and simply
#   check if you own the magic. If you own it, you'll likely own the others.
m.newDmg(50)
m.newTrig('spellowned',"Feeding Frenzy")
m.newDmg(50+25*5)
m.newTrigTag('aquatic')
m.newDmg(100)
m.newProc(9)
#
m = Magic("Enraged Feeding Frenzy","EFF")
#   Checks for ownership of Monster Fisherman and Fish Hooks. Not doing that.
#   Since its damage is so significant, we'll do the cheap way out and simply
#   check if you own the magic. If you own it, you'll likely own the others.
m.newDmg(50)
m.newTrig('spellowned',"Enraged Feeding Frenzy")
m.newDmg(100+30*5)
m.newTrigTag('aquatic')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Deep Freeze","deep")  #avoiding name collision with Dark Forest
#   This checks for a bunch of guild stuff. Let's cheat and say that if you own
#   the magic, you'll probably have tortured yourself into getting the rest too.
m.newDmg(50)
m.newTrig('spellowned',"Deep Freeze")
m.newDmg(10*4+15*3)
m.newTrigTag('aquatic')
m.newDmg(100)
m.newProc(13)
#
m = Magic("Fury of the Deep","FotD")
m.newDmg(10)
m.newTrigTag('aquatic')
m.newDmg(45)
m.newTrigTag('aquatic')
m.newDmg( lambda : 30 if OWNED["KATH'IN"] else 0 )
m.newProc(100)
#
m = Magic("Unity","uni")
m.newDmg(50)
m.newTrig('spellcast',"Deathmark")
m.newDmg(50)
m.newTrig('spellcast',"Volatile Runes")
m.newDmg(50)
m.newTrigTag('guild')
m.newDmg(300)
m.newProc(20)
#
m = Magic("Deathmark","DM")
m.newDmg(100)
m.newTrig('spellowned',"Deathmark")
m.newDmg(100)
m.newTrigTag('guild')
m.newDmg(190)
m.newProc(11)
#
m = Magic("Rally","rally")
#   This wants you to calc for # of Spirit Raven set pieces owned. Not doing it.
m.newTrigTag('guild')
m.newDmg(120)
m.newTrig('spellcast',["Unity","Deathmark","Volatile Runes"])
m.newDmg(200)
m.newProc(6)
#
m = Magic("Volatile Runes","VR")
m.newDmg(100)
m.newTrig('spellowned',"Volatile Runes")
m.newDmg(200)
m.newTrig('spellcast',"Volatile Runes")
m.newDmg(100)
m.newTrigTag('guild')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Weightlessness","weight")
m.newDmg(100)
m.newTrig('spellowned',"Weightlessness")
m.newDmg(100)
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Avalanche","ava")
m.newDmg(100)
m.newTrigTag('winter')
m.newDmg(350)
m.newTrigTag('siege')
m.newDmg(200)
m.newTrigTag('siege')
m.newTrig('spellcast',"Weightlessness")
m.newDmg(300)
m.newProc(10)
#
m = Magic("Beach","beach")
m.newDmg(100)
m.newTrigTag('abyssal')
m.newDmg(100)
m.newTrigTag('aquatic')
m.newDmg(100)
m.newTrigTag('terror')
m.newDmg(100)
m.newTrigTag('insect')
m.newDmg(100)
m.newProc(10)
#
m = Magic("Annus Mirabilis","AM")
m.newDmg(34)
m.newProc(12)
#
m = Magic("Begone, Fiends!","BF")
m.newTrigTag('demon')
m.newDmg(150)
m.newProc(5)
m.newTrigTag('demon')
m.newTrig('spellcast',"Hell's Knell")
m.newDmg(210)
m.newProc(2)
m.newTrigTag('demon')
m.newTrig('spellcast',"Hell's Knell")
m.newDmg(210)
m.newProc(2)
#
m = Magic("Blood Moon","BM")
#   Wants to check for three different generals. No way.
m.newDmg(100)
m.newTrig('spellowned',"Glimmering Moon")
m.newDmg(50)
m.newTrigTag('human')
m.newDmg(100)
m.newProc(10)
#
m = Magic("Bramblewire Trap","BT")
#   Checks for Battle-Scarred set and others. Wow. No. Not just no, but hell no.
m.newDmg(60)
m.newTrigTag('goblin')
m.newDmg(200)
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Briseis' Blessing","BB")
m.newDmg(1)
m.newTrig('spellcast',"Chryseis' Kiss")
m.newTrigTag('dragon')
m.newDmg(200)
m.newProc(5)
#
m = Magic("Burning Rain","BR")
m.newDmg(3)
m.newProc(100)
#
m = Magic("Cast Down","CD")
m.newTrigTag('dragon')
m.newDmg(125)
m.newTrigTag('demon')
m.newDmg(175)
m.newProc(14)
#
m = Magic("Celestial Catapult","CC")
m.newDmg(5)
m.newTrig('spellcast',"Infernal Bombardment")
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(5)
#
m = Magic("Consume","cons")
#   Most of the damage comes from checking if Burut the Hungry is owned, and if
#   the other mounts from Horn of Plenty is owned. This is such a thing, so
#   let's just assume you own it all if you have the magic. It'll be cheaper.
m.newDmg(120)
m.newTrig('spellowned',"Consume") #workaround
m.newDmg(40+5*(5*3))
m.newProc(15)
#
m = Magic("Corpse Explosion","CEx")
m.newTrigTag('undead')
m.newDmg(250)
m.newTrig('spellcast',"Holy Nova")
m.newTrigTag('undead')
m.newDmg(175)
m.newTrig('spellcast',"Soul Pilferer")
m.newTrigTag('undead')
m.newDmg(175)
m.newProc(15)
#







'''
m = Magic("","")
m.newDmg()
m.newTrig('spellcast',"")
m.newTrig('spellowned',"")
m.newTrigTag('')
m.newDmg()
m.newProc()
'''

        
#RAIDTAGS.append('dragon')  #DEBUG
print "Raid magic, calc for tags: "+str(RAIDTAGS)


print "-------------"
# Get noncast averages of each spell into ALLMAGICS list.
ALLMAGICS = []
for i in Magic.spelllist:
    avg = i.getAvg()
    ALLMAGICS.append([i,avg])
    if SHOWDEBUG: print "Magic: "+str(i.nickname)+", avg dmg: "+str(avg)
#Sort ALLMAGICS and skim off top into MAGICLIST to start calc for NEWMAGICS
ALLMAGICS = sorted(ALLMAGICS,key = lambda x: x[1],reverse = True)
MAGICLIST = copy.deepcopy(ALLMAGICS[:SLOTNUM+5])
NEWMAGICS = []
for i,oavg in MAGICLIST:
    avg = i.getAvg()
    NEWMAGICS.append([i,avg])
NEWMAGICS = sorted(NEWMAGICS,key = lambda x: x[1],reverse = True)
#And now we should have a roughly optimized table.

shortlist = ""
for idx,i in enumerate(range(SLOTNUM+5)):
    spell = NEWMAGICS[i][0]
    avg   = NEWMAGICS[i][1]
    if idx==SLOTNUM: print "-------------"
    print str(spell.fullname)+": "+str(avg)
    shortlist += spell.nickname
    if idx==(SLOTNUM-1):
        shortlist += ';'
    else:
        shortlist += ','
print "-------------"
print "Short list:"
shortlist = shortlist[:-1]
print shortlist

