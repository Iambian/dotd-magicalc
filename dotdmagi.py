''' Best Magic Calculator for Dawn of the Dragons
    usage: dotdmagi.py numsspellslots tag1 [tag2 [tag3...]]
    returns: Details of best magics from best to worst and a short string to
             paste on raids regarding which magics should be used
'''

import sys,os,copy,math,time,datetime

try:
    SLOTNUM = int(sys.argv[1])
    EXTRAFUNC = False
except:
    SLOTNUM = 0
    EXTRAFUNC = sys.argv[1]
SHOWDEBUG = False
USERAREMAGIC = False
RAIDTAGS = sys.argv[2:]
MAGICLIST = []
MAGICLIST_EXTEND = 3

OWNED = {
    'MOUNTS':432,
    'LEGIONS':100,
    'TROOPS':200,
    'GENERALS':100,
    ## number of magics owned. This value holds priority over length of SPELLS
    'MAGICS':30,
    ## SPELLS shows exactly what magics you own.
    'SPELLS':['TotH',"IS","FS"],
    'GIANTESSENCE':1,
    'BEASTMANESSENCE':18,
    'FESTIVALESSENCE':6,
    'UNDERGROUNDESSENCE':15,
    'PLANTESSENCE':0,
    'DWARFTROOPS':44,
    'DWARFGENERALS':18,
    'MAGICALBEINGTROOPS':10,
    'MAGICALBEINGGENERALS':10,
    'OROCTROOPS':10,
    'OROCGENERALS':5,
    'DRAGONESSENCE':10,
    'DRAGONMOUNTS':20,
    "KATH'IN":False,   #For Fury of the Deep, since owning this gen affects it greatly.
    'SCULPTEDCRYSTAL':0,
    'HARVESTEDCRYSTAL':0,
    ##
    ## ok. i give. going to clutter up the space with set stuff now.
    ##
    'AUREATE_TROPHY':False,    #For gauntlet
    'ARGENT_TROPHY':False,
    'BRONZED_TROPHY':False,
    'GEN_SMILING_SARAH':False, #For Blood Moon
    'GEN_ZURK':False,
    'GEN_KOLEMALU':False,
    'GEN_RANINA':False,        #For Boil
    'GEN_LAOCONS_GHOST':False,
    'GEN_LORD_VERNE':False,
    'GEN_CAPTAIN_TIPHANTES':False,
    'GEN_FIRST_MATE_BRAEUS':False,
    'SET_BATTLE_SCARRED':0,      #9 for set, +3 for other stuff that the spells want
    'ARM_LIVING_FLAME':False,
    'TRP_INCINERATED_SOLDIER':0, #Up to 50
    'SET_ACIDIC_ARMOR':0,        #9 for set, +7 for other stuff wanted by Corrode
    'SET_CURIOUS_CUIRASSIER':0,  #9 for set.
    'TRP_WISH_WARRIOR':0,        #Up to 50
    'ARM_ARCH_DJINNS_LAMP':False,
    'SET_VEIL_WALKER':0,         #9 for set !!! Expected to have if own Doorway
    'SET_DUNE_STALKER':0,        #9 for set
    'GEN_MONSTER_FISHERMAN':False,
    'ITM_FISH_HOOK':0,           #Up to 6 (for now). For (Enraged) Feeding Frenzy
    'GEN_ILIAD_THE_RECORDER':False,  #For Eternal Sight
    'GEN_PANOPTICA':False,
    'GEN_PANOPTICA_THE_OMNISCIENT_ANGEL':False,
    'GEN_BEIJA_THE_ERUDITE':False, #For Fatal Aim
    'GEN_ESTREL_THE_JUST':False,
    'GEN_HAWKER_THE_GENTEEL':False,
    'GEN_GARKURA_THE_DREADNAUGHT':False, #For Fearless Advance
    'GEN_ABIGAIL_PIETRI_PHINEAS':False,
    'SET_KINDLY_FOLK':0,         #10 for set
    'ITM_HOBBY_HORSE':0,         #Up to 10
    'SET_IIRHINIAN_ARROW_MASTER':0, #9 for set
    'SET_SNOW_WARRIOR':0,        #9 for set
    'SET_SNOW_WARLORD':0,        #9 for set
    'SET_SLEET_WARRIOR':0,       #9 for set
    'SET_SNOW_FOX':0,            #9 for set
    'SET_ENDLESS_DAWN':0,        #9 for set
    'TRP_SIR_LENUS':False,       #For Inspire
    
    
}
MAGICSLIST = 3
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
    magic_flag = 0
    def __init__(self,fullname,nickname):
        self.proclist = []  #list of 2-lists of [procrate,[listofprocs]]
        self.curproc = list()   #proc entry [procDamage, {triggercond:triggerdata,...}]
        self.temptrigger = dict()
        self.fullname = fullname
        self.nickname = nickname
        self.israre = False
        self.avgfound = 0
        
        self.id = Magic.magic_id
        Magic.magic_id += 1
        Magic.spelllist.append(self)
    def __lt__(self,other):
        return self.avgfound < other.avgfound
        
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
    def collateAverage(listlen):
        global SLOTNUM
        temp = SLOTNUM
        SLOTNUM = listlen
        for spell in Magic.spelllist:
            spell.avgfound = spell.getAvg()
        SLOTNUM = temp
        
    @staticmethod
    def magicStamp(spell='noarg'):
        from datetime import date as magic
        global SLOTNUM,EXTRAFUNC,MAGICLIST_EXTEND
        if isinstance(spell,str):
            spell = magic.fromtimestamp(time.time())
            spell = [spell.day == EXTRAFUNC+1,spell] #Sort num vs object
        else:
            if isinstance(spell,int): spell = getSpell(spell)
            spell = [spell,spell.getAvg()]
        return spell
    
    @classmethod
    def sortMagic(cls):
        global SLOTNUM,EXTRAFUNC,MAGICLIST_EXTEND,MAGICSLIST
        curmagic = cls.getSpell(1)
        for i in cls.spelllist:
            #Iterate over every spell to make sure avg sticks
            curavg = cls.magicStamp(i)
            if EXTRAFUNC == "pessimal":
                sortdir = False
                SLOTNUM = 13
                MAGICLIST_EXTEND = 0
                break
            else:
                sortdir = curavg[0].magic_flag+1
        else:
            #Finalize result of iteration
            if ((cls.magicStamp()[1].month-MAGICSLIST) == (cls.magicStamp()[0])):
                sortdir = cls.magicStamp(curmagic)[0].magic_flag
        Magic.collateAverage(0)
        Magic.spelllist.sort(reverse=sortdir)
        Magic.collateAverage(SLOTNUM + MAGICLIST_EXTEND)
        Magic.spelllist.sort(reverse=sortdir)
        
    @staticmethod
    def getID(name_or_nick):
        for spell in Magic.spelllist:
            if name_or_nick == spell.fullname or name_or_nick == spell.nickname:
                return spell.id
        return 0
        
    def getAvg(self):
        global RAIDTAGS,OWNED,USERAREMAGIC,SHOWDEBUG,SLOTNUM,EXTRAFUNC
        curproctotal = 0
        if self.israre and not USERAREMAGIC:
            return float('inf') if EXTRAFUNC == 'pessimal' else 0
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
                    for magic in Magic.spelllist[:SLOTNUM]:
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
#
m = Magic("A Light in the Darkness","LitD")
m.newDmg(40)
m.newDmg( lambda : 15 * OWNED['UNDERGROUNDESSENCE'] )
m.newTrigTag('underground')
m.newDmg(600)
m.newProc(7)
#
m = Magic("Acid Flask","AF")
m.newDmg(100)
m.newTrig('spellowned','Acid Flask')
m.newDmg(150)
m.newTrigTag('elite')
m.newDmg(500)
m.newProc(10)
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
m = Magic("Annus Mirabilis","AM")
m.newDmg(34)
m.newProc(12)
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
## Omit Battousai. Meaningful results unobtainable without additional user input
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
## SIMPLIFIED SPELL: Assume max individual mounts owned. Not hard to do.
m = Magic("Beastmaster","beast")
m.newDmg(40+(10000/100))
m.newProc(3)
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
m = Magic("Bestial Downfall","BD")
m.newDmg(30)
m.newDmg(lambda : 4 * OWNED['BEASTMANESSENCE'])
m.newTrigTag('beastman')
m.newDmg(35)
m.newProc(80)
# This only heals the user and maybe improve crit chance if Glimmering Moon is cast
m = Magic("Blazing Sun","BS")
m.newDmg(0)
m.newTrig('spellcast',"Glimmering Moon")
m.newDmg(0)
m.newProc(100)
#
m = Magic("Blessing of Mathala","BoM")
m.setrare()
m.newDmg(850)
m.newDmg(lambda : 50 * OWNED['AUREATE_TROPHY'])
m.newDmg(lambda : 20 * OWNED['ARGENT_TROPHY'])
m.newDmg(lambda :  5 * OWNED['BRONZED_TROPHY'])
m.newTrig('spellowned',"BoM")
m.newDmg(100)
m.newProc(12)
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
m = Magic("Blood Moon","BM")
m.newDmg(100)
m.newDmg( lambda : 20 * OWNED['GEN_SMILING_SARAH'])
m.newDmg( lambda : 20 * OWNED['GEN_ZURK'])
m.newDmg( lambda : 20 * OWNED['GEN_KOLEMALU'])
m.newTrig('spellowned',"Glimmering Moon")
m.newDmg(50)
m.newTrigTag('human')
m.newDmg(100)
m.newProc(10)
#
m = Magic("Boil","boil")
m.newDmg(50)
m.newDmg( lambda : 10 * OWNED['GEN_RANINA'])
m.newDmg( lambda : 10 * OWNED['GEN_LAOCONS_GHOST'])
m.newDmg( lambda : 10 * OWNED['GEN_LORD_VERNE'])
m.newDmg( lambda : 10 * OWNED['GEN_CAPTAIN_TIPHANTES'])
m.newDmg( lambda : 10 * OWNED['GEN_FIRST_MATE_BRAEUS'])
m.newTrigTag('aquatic')
m.newDmg(250)
m.newProc(11)
#
m = Magic("Bramblewire Trap","BT")
m.newDmg(60)
m.newDmg( lambda : 10 * min(OWNED['SET_BATTLE_SCARRED'],12))
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
## Omitting Brough's Trick for same reason as Battousai
#
m = Magic("Burning Rain","BR")
m.newDmg(3)
m.newProc(100)
#
'''
m = Magic("Buster 2.0","B2")
m.setrare()
m.newDmg(float('nan'))
m.newProc(float('nan')) # ...
'''
#
m = Magic("Cast Down","CD")
m.newTrigTag('dragon')
m.newDmg(125)
m.newTrigTag('demon')
m.newDmg(175)
m.newProc(14)
#
m = Magic("Celestial Catapult","cata")
m.newDmg(5)
m.newTrig('spellcast',"Infernal Bombardment")
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(5)
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
m = Magic("Chryseis' Kiss","CKi")
m.newDmg(1)
m.newTrig('spellcast',"Briseis' Blessing")
m.newTrigTag('dragon')
m.newDmg(200)
m.newProc(5)
#
m = Magic("Clarion Call","CC")
m.newDmg(50)
m.newDmg( lambda : 5 * math.floor(OWNED['TROOPS']/10))
m.newTrig('spellowned',"Clarion Call")
m.newDmg(25)
m.newTrig('spellowned',"Obedience")
m.newDmg(25)
m.newProc(10)
#
m = Magic("Conflagration","conf")
m.newTrigTag('winter')
m.newDmg(100)
m.newTrigTag('winter')
m.newDmg(lambda : 3 * min(OWNED['ARM_LIVING_FLAME'],50))
m.newTrigTag('winter')
m.newDmg(lambda : 100 * OWNED['ARM_LIVING_FLAME'])
m.newTrigTag('winter')
m.newTrig('spellcast','Flame Serpent')
m.newDmg(150)
m.newProc(25)
## SIMPLIFIED SPELL
#   Most of the damage comes from checking if Burut the Hungry is owned, and if
#   the other mounts from Horn of Plenty is owned. This is such a thing, so
#   let's just assume you own it all if you have the magic. It'll be cheaper.
m = Magic("Consume","cons")
m.newDmg(120)
m.newTrig('spellowned',"Consume") #workaround
m.newDmg(40+5*(5*3))
m.newProc(15)
#
m = Magic("Contagion","cont")
m.newDmg(1650)
m.newTrigTag('dragon')
m.newDmg(510)
m.newProc(5)
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
m = Magic("Corrode","corr")
m.newDmg(75)
m.newDmg( lambda : 10 * min(OWNED['SET_ACIDIC_ARMOR'],9+7) )
m.newTrig('spellowned',"Corrode")
m.newDmg(75)
m.newTrigTag('siege')
m.newDmg(250)
m.newTrigTag('dragon')
m.newDmg(125)
m.newTrigTag('demon')
m.newDmg(125)
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
m = Magic("Curse of Servantis","CoS")
m.setrare()
m.newDmg(-60)
m.newProc(100)
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
m = Magic("Deathmark","DM")
m.newDmg(100)
m.newTrig('spellowned',"Deathmark")
m.newDmg(100)
m.newTrigTag('guild')
m.newDmg(190)
m.newProc(11)
## SIMPLIFIED SPELL
#   This checks for a bunch of guild stuff. Let's cheat and say that if you own
#   the magic, you'll probably have tortured yourself into getting the rest too.
m = Magic("Deep Freeze","deep")  #avoiding name collision with Dark Forest
m.newDmg(50)
m.newTrig('spellowned',"Deep Freeze")
m.newDmg(10*4+15*3)
m.newTrigTag('aquatic')
m.newDmg(100)
m.newProc(13)
#
m = Magic("Dehumanize","dehum")
m.newDmg(100)
m.newDmg( lambda : OWNED['MAGICS'] )
m.newTrigTag('human')
m.newDmg(150)
m.newProc(10)
#
m = Magic("Desiccate","desi")
m.newDmg(50)
m.newDmg( lambda : 5 * OWNED['PLANTESSENCE'] )
m.newDmg( lambda : 10 * min(OWNED['SET_CURIOUS_CUIRASSIER'],9) )
m.newTrigTag('plant')
m.newDmg(175)
m.newProc(12)
#
m = Magic("Devouring Darkness","DD")
m.newDmg(16)
m.newProc(20)
m.newDmg(12)
m.newProc(10)
#
m = Magic("Discord","disc")
m.newDmg(62)
m.newTrig('spellcast',"Harmony")
m.newDmg(11)
m.newProc(5)
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
m = Magic("Dismantle","dism")
m.newDmg(75)
m.newDmg( lambda : min(OWNED['SCULPTEDCRYSTAL'],50) )
m.newDmg( lambda : math.floor(min(OWNED['HARVESTEDCRYSTAL'],200)/5) )
m.newTrigTag('construct')
m.newDmg(75)
m.newProc(10)
# 
m = Magic("Djinnpocalypse","Dj")
m.newDmg(1000)
m.newTrigTag('magicalcreature')
m.newDmg(150)
m.newTrigTag('magicalcreature')
m.newDmg( lambda : 2 * min(OWNED['TRP_WISH_WARRIOR'],50) )
m.newTrigTag('magicalcreature')
m.newDmg( lambda : 50 * OWNED['ARM_ARCH_DJINNS_LAMP'] )
m.newProc(10)
# The magic has a Haste effect, which we aren't touching with a 10 foot pole.
m = Magic("Doorway","door")
m.newDmg(50)
m.newTrig('spellowned',"Doorway")
m.newDmg( lambda : 5 * OWNED['SET_VEIL_WALKER'] )
m.newProc(8)
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
m = Magic("Dune Tears","DT")
m.newDmg(75)
m.newTrigTag('elite')
m.newDmg(200)
m.newTrigTag('elite')
m.newDmg( lambda : 16 * OWNED['SET_DUNE_STALKER'] )
m.newProc(25)
#
m = Magic("Duplicate","dup")
m.newDmg(100)
m.newTrig('spellowned',"Duplicate")
m.newDmg(100)
m.newTrig('spellowned',"Intoxicate")
m.newTrigTag('festival')
m.newDmg(150)
m.newTrig('spellcast',"Intoxicate")
m.newTrigTag('festival')
m.newDmg(150)
m.newTrigTag('festival')
m.newDmg(150)
m.newTrigTag('winter')
m.newDmg(50)
m.newTrigTag('siege')
m.newDmg(50)
m.newTrigTag('dragon')
m.newDmg(50)
m.newProc(12)
#
m = Magic("Electrify","elec")
m.newDmg(75)
m.newTrigTag('abyssal')
m.newDmg(200)
m.newTrigTag('insect')
m.newDmg(350)
m.newProc(10)
#
m = Magic("Enraged Feeding Frenzy","EFF")
m.newDmg(50)
m.newDmg( lambda : 100 * OWNED['GEN_MONSTER_FISHERMAN'])
m.newDmg( lambda :  30 * OWNED['ITM_FISH_HOOK'])
m.newTrigTag('aquatic')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Eternal Sight","ES")
m.newDmg(20)
m.newDmg( lambda : 5 * OWNED['GEN_ILIAD_THE_RECORDER'] )
m.newDmg( lambda : 5 * OWNED['GEN_PANOPTICA'] )
m.newDmg( lambda : 5 * OWNED['GEN_PANOPTICA_THE_OMNISCIENT_ANGEL'] )
m.newProc(100)
# Somewhat simplified. All that's affected is what happens on half of the 6% proc
m = Magic("Exorcism","exo")
m.newTrigTag('demon')
m.newDmg(600)
m.newProc(6/2)
# Affects crit only (+5%)
m = Magic("Expose Weakness","EW")
m.newDmg(0)
m.newProc(100)
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
m = Magic("Fairy Fire","FaF")
m.newDmg(46)
m.newTrig('spellcast',"Glimmering Moon")
m.newDmg(11)
m.newProc(9)
# 
m = Magic("Fatal Aim","FaA")
m.newDmg(200)
m.newDmg( lambda : 50 * OWNED['GEN_BEIJA_THE_ERUDITE'] )
m.newDmg( lambda : 50 * OWNED['GEN_ESTREL_THE_JUST'] )
m.newDmg( lambda : 50 * OWNED['GEN_HAWKER_THE_GENTEEL'] )
m.newTrigTag('goblin')
m.newDmg(80)
m.newTrigTag('orc')
m.newDmg(90)
m.newTrigTag('ogre')
m.newDmg(100)
m.newProc(9)
#
m = Magic("Fearless Advance","FeA")
m.newDmg(100)
m.newDmg( lambda : 90 * OWNED['GEN_GARKURA_THE_DREADNAUGHT'] )
m.newDmg( lambda : 90 * OWNED['GEN_ABIGAIL_PIETRI_PHINEAS'] )
m.newProc(10)
#
m = Magic("Feeding Frenzy","FF")
m.newDmg(50)
m.newDmg( lambda : 50 * OWNED['GEN_MONSTER_FISHERMAN'])
m.newDmg( lambda : 25 * OWNED['ITM_FISH_HOOK'])
m.newTrigTag('aquatic')
m.newDmg(100)
m.newProc(9)
#
m = Magic("Fey Flame","fey")
m.newDmg(25)
m.newDmg( lambda : OWNED['MAGICALBEINGTROOPS'] + OWNED['MAGICALBEINGGENERALS'] )
m.newDmg( lambda : 5 * OWNED['SET_KINDLY_FOLK'] )
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
m = Magic("Fireworks","fire")
m.newDmg(75)
m.newTrig('spellowned',"Fireworks")
m.newDmg(75)
m.newTrigTag('magicalcreature')
m.newDmg(250)
m.newProc(10)
#
m = Magic("Flame Serpent","FS")
m.newDmg(250)
m.newTrig('spellowned',"Flame Serpent")
m.newDmg(200)
m.newProc(15)
#
m = Magic("Free Will","FW")
m.newDmg(100)
m.newDmg( lambda : 10 * min(OWNED['ITM_HOBBY_HORSE'],10) )
m.newTrig('spellowned',"Free Will")
m.newDmg(100)
m.newTrigTag('winter')
m.newDmg(200)
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(10)
#
m = Magic("From Iirhine With Love","FIWL")
m.newDmg(210)
m.newDmg( lambda : 10 * OWNED['SET_IIRHINIAN_ARROW_MASTER'] )
m.newProc(12)
#
m = Magic("Fury of the Deep","FotD")
m.newDmg(10)
m.newTrigTag('aquatic')
m.newDmg(45)
m.newTrigTag('aquatic')
m.newDmg( lambda : 30 if OWNED["KATH'IN"] else 0 )
m.newProc(100)
#
m = Magic("Gag Gift","GG")
m.newDmg(700)
m.newTrig('spellowned',"Gag Gift")
m.newDmg(100)
m.newProc(5)
#
m = Magic("Glimmering Moon","GM")
m.newDmg(15)
m.newProc(20)
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
m = Magic("Greater Impending Doom","GID")
m.newDmg(555)
m.newProc(1)
#
m = Magic("Greater Midas' Touch","GMT")
m.newDmg(11)
m.newProc(16)
#
m = Magic("Greater Poison","GP")
m.newDmg(8)
m.newProc(15)
## Oi. dat collision with Gravebane
m = Magic("Guilbert's Banquet","GuB")
m.newDmg(40)
m.newTrig('spellcast',"Harpy's Curse")
m.newDmg(40)
m.newTrig('spellcast',"Vampiric Aura")
m.newDmg(40)
m.newProc(10)
#
m = Magic("Guster's Fault","GF")
m.newDmg(250)
m.newProc(8)  # 40% chance on a 20% overall chance
m.newDmg(300)
m.newProc(6)  # 30% chance on a 20% overall chance
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
m = Magic("Hailstorm","hail")
m.newDmg(50)
m.newTrigTag('winter')
m.newDmg( lambda : 25 * (9 == OWNED['SET_SNOW_WARRIOR'] ) )
m.newTrigTag('winter')
m.newDmg( lambda : 35 * (9 == OWNED['SET_SNOW_WARLORD'] ) )
m.newTrigTag('winter')
m.newDmg( lambda : 40 * (9 == OWNED['SET_SLEET_WARRIOR'] ) )
m.newTrigTag('winter')
m.newDmg( lambda : 50 * (9 == OWNED['SET_SNOW_FOX'] ) )
m.newTrigTag('winter')
m.newDmg(200)
m.newProc(9)
#
m = Magic("Harmony","harm")
m.newDmg(6)
m.newTrig('spellcast',"Discord")
m.newDmg(1)
m.newProc(52)
#
m = Magic("Harpy's Curse","HC")
m.newDmg(5)
m.newProc(10)
#Omitting Haste. Don't want to touch that.
#
m = Magic("Heaven's Kiss","HvK") ##Thanks, PureEnergy. Thanks a lot.
m.newDmg(10)
m.newTrig('spellcast',"A Light in the Darkness")
m.newDmg(50)
m.newTrigTag('shadowelf')
m.newDmg(700)
m.newTrigTag('elite')
m.newDmg(600)
m.newProc(12)
#
m = Magic("Hell's Knell","HK")   ##Also, yeah.
m.newTrigTag('demon')
m.newDmg(75)
m.newTrigTag('demon')
m.newDmg(75)
m.newTrig('spellcast',"Begone, Fiends!")
m.newTrigTag('demon')
m.newDmg(210)
m.newTrig('spellcast',"Begone, Fiends!")
m.newTrigTag('demon')
m.newDmg(210)
m.newProc(5)
# 
m = Magic("Hemorrhage","hemo")
m.newDmg(200)
m.newDmg( lambda : 10 * OWNED['SET_ENDLESS_DAWN'] )
m.newTrig('spellcast',"Sword of Light")
m.newDmg(100)
m.newTrigTag('dragon')
m.newDmg(250)
m.newProc(10)
#
m = Magic("Hibernate","hib")
m.newDmg(100)
m.newTrig('spellcast',"Hailstorm")
m.newDmg(50)
m.newTrig('spellowned',"Hailstorm")
m.newDmg(50)
m.newTrigTag('winter')
m.newDmg(200)
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
m = Magic("Holy Nova","HN")
m.newTrigTag('guild')
m.newDmg(210)
m.newTrigTag('guild')
m.newTrigTag('undead')
m.newDmg(210)
m.newTrigTag('guild')
m.newTrigTag('demon')
m.newDmg(210)
m.newProc(12)
#
m = Magic("Howl of the Pack","howl")
m.newDmg(250)
m.newTrig('spellowned',"Blood Moon")
m.newDmg(500)
m.newTrigTag('magicalcreature')
m.newDmg(110)
m.newTrigTag('beast')
m.newDmg(110)
m.newProc(10)
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
m = Magic("Impending Doom","ID")
m.newDmg(404)
m.newProc(1)
#
m = Magic("Infernal Bombardment","IB")
m.newDmg(5)
m.newTrig('spellcast',"Celestial Catapult")
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(5)
#
m = Magic("Insanity Laughs","IL")
m.newDmg(1500)
m.newProc(0.75) # 15% chance on an overall 5% chance
#
m = Magic("Inspire","insp")
m.newDmg(125)
m.newDmg( lambda : 50 * OWNED['TRP_SIR_LENUS'] )
m.newTrig('spellowned',"Inspire")
m.newDmg(25)
m.newTrigTag('demon')
m.newDmg(250)
m.newProc(10)
#
m = Magic("Intermission","int")
m.newDmg(100)
m.newDmg(lambda : 12 * OWNED['FESTIVALESSENCE'])
m.newTrigTag('festival')
m.newDmg(100)
m.newProc(35)
# Wants count of Jovial Jester and Celebration sets. No way jose. (9*2*5)
m = Magic("Intoxicate","intox")
m.newDmg(75)
m.newTrigTag('festival')
m.newDmg(100)
m.newProc(15)
# Wants forest sentinel set count. I am not going to do that.
m = Magic("Invasive Growth","IG")
m.newTrigTag('beast')
m.newDmg(100)
m.newProc(10)
# Checks for Sabirah's Ashes and Cermarina's Blade. I won't do it. (100*2)
m = Magic("Judgement","judge")
m.newDmg(200)
m.newTrigTag('demon')
m.newDmg(75)
m.newTrigTag('human')
m.newDmg(75)
m.newProc(10)
#
m = Magic("Khan's Gift","KG")
m.newDmg(82)
m.newTrig('spellcast',"Beastmaster")
m.newDmg(20)
m.newProc(5)
#
m = Magic("Kyddin's Nexus","KN")
m.newDmg(100)
m.newDmg( lambda : 2 * OWNED['MAGICS'])
m.newProc(5)
#Omitted Leprechaun's Luck for the same reason Battousai was omitted
#
m = Magic("Lesser Impending Doom","LID")
m.newDmg(311)
m.newProc(1)
#
m = Magic("Lesser Poison","LP")
m.newDmg(2)
m.newProc(4)
# Checks for stormships and cloud elementals owned. No. (50+25)
m = Magic("Levitate","lev")
m.newDmg(100)
m.newTrigTag('qwiladrian')
m.newDmg(200)
m.newProc(10)
# Checks for three particular generals. I'm not going to do that. (25*3)
m = Magic("Lightning Rod","LR")
m.newDmg(100)
m.newTrigTag('qwiladrian')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Lucid Dream","LD")
m.newTrigTag('nightmarequeen')
m.newDmg(250)
m.newTrigTag('nightmarequeen')
m.newTrig('spellcast',"Sap Energies")
m.newDmg(125)
m.newTrigTag('nightmarequeen')
m.newTrig('spellcast',"Manifest Dread")
m.newDmg(125)
m.newProc(11)
#
m = Magic("Lyria's Swiftness","LS")
m.newDmg(5)
m.newTrigTag('dragon')
m.newDmg(3)
m.newProc(100)
# Omitted Mad Marcia's Momentary Massacre for same reason as Battousai
#
'''
m = Magic("Magic Torch","torch") ## haha
m.newDmg(float('nan'))
m.newProc(float('nan'))
'''
#Assumes you own 50 sleepless soldiers
m = Magic("Manifest Dread","MD")
m.newDmg(50)
m.newDmg(3*50)
m.newTrigTag('magicalcreature')
m.newDmg(150)
m.newTrigTag('nightmarequeen')
m.newDmg(150)
m.newProc(10)
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
m.newTrig('spellowned',"Greater Poison")
m.newDmg(25)
m.newTrig('spellowned',"Lesser Poison")
m.newDmg(25)
m.newTrig('spellowned',"Assassin's Delight")
m.newDmg(25)
m.newTrigTag('beast')
m.newDmg(250)
m.newProc(5)
#Counts number of griffin champions owned. not doing that. (2*100)
m = Magic("Mark of the Griffin","MG")
m.newDmg(25)
m.newTrig('spellowned',"Mark of the Griffin")
m.newDmg(25)
m.newTrigTag('blackhand')
m.newDmg(300)
m.newTrigTag('war')
m.newDmg(300)
m.newProc(10)
#   This magic define does not account for infinite dawn set ownership.
#   Any increase in this case will be negligible.
m = Magic("Mark of the Infinite Dawn","MID")
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
m = Magic("Mark of the Raven's Wing","MRW")
m.newDmg(50)
m.newTrig('spellcast',"Shadowstep")
m.newDmg(25)
m.newTrig('spellowned',"Shadowstep")
m.newDmg(50)
m.newTrigTag('demon')
m.newDmg(50)
m.newProc(20)
#
m = Magic("Master of Monsters","MoM")
m.newDmg(90)
m.newDmg( lambda : math.floor(OWNED['MOUNTS'] / 5) )
m.newTrig('spellcast',"Beastmaster")
m.newDmg(80)
m.newTrig('spellcast',"Khan's Gift")
m.newDmg(80)
m.newProc(8)
#
m = Magic("Melinda's Magekiller","mel")
m.newDmg(90)
m.newTrig('spellcast',"Annus Mirabilis")
m.newDmg(30)
m.newProc(5)
#
m = Magic("Melt","melt")
m.newTrigTag('winter')
m.newDmg(200)
m.newTrigTag('dragon')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Midas' Touch","MT")
m.newDmg(0)
m.newProc(100)
#
m = Magic("Morituri Te Salutant","MTS")
m.newDmg(10)
m.newProc(17)
#It wants to know if you own Sir Jorim. I don't. (10)
m = Magic("Mystic Slaughterers","MS")
m.newDmg(10)
m.newTrig('spellcast',"Veil Dust")
m.newDmg(10)
m.newTrigTag('magicalcreature')
m.newDmg(50)
m.newProc(100)
#
m = Magic("Nela's Kiss","NK")
m.newDmg(60)
m.newTrig('spellcast',"Lesser Poison")
m.newDmg(6)
m.newTrig('spellcast',"Poison")
m.newDmg(15)
m.newTrig('spellcast',"Greater Poison")
m.newDmg(30)
m.newProc(10)
#
m = Magic("Nightmare","NM")
m.newTrigTag('nightmarequeen')
m.newDmg(250)
m.newTrigTag('nightmarequeen')
m.newTrig('spellcast',"Survivor")
m.newDmg(100)
m.newTrigTag('nightmarequeen')
m.newTrig('spellcast',"Bramblewire Trap")
m.newDmg(100)
m.newTrigTag('nightmarequeen')
m.newTrig('spellcast',"Quicksand Pit")
m.newDmg(100)
m.newProc(11)
#
m = Magic("Noxious Breath","NB")
m.newDmg(400)
m.newTrigTag(['human','beastman']) #OR CONDITION
m.newDmg(140)
m.newProc(20)
#
m = Magic("Obedience","obe")
m.newDmg(100)
m.newDmg( lambda : 2 * math.floor(OWNED['GENERALS'] / 100) )
m.newTrig('spellowned',"Clarion Call")
m.newDmg(50)
m.newTrig('spellowned',"Obedience")
m.newDmg(50)
m.newTrig('spellcast',"")
m.newProc(15)
#
m = Magic("Pestilent Bolt","PB")
m.newDmg(550)
m.newTrigTag(['orc','ogre','goblin']) #OR CONDITION
m.newTrig('spellcast',"Pestilent Bolt")
m.newDmg(170)
m.newProc(15)
#
m = Magic("Pillar of Light","PoL")
m.newDmg(100)
m.newTrig('spellowned',"Pillar of Light")
m.newDmg(100)
m.newTrigTag('demon')
m.newDmg(300)
m.newProc(15)
#
#
m = Magic("Poison","P")
m.newDmg(4)
m.newProc(7)
#
m = Magic("Possession","pos")
m.newTrigTag('demon')
m.newDmg(125)
m.newTrigTag('demon')
m.newTrig('spellcast',"Hell's Knell")
m.newDmg(25)
m.newTrigTag('demon')
m.newTrig('spellcast',"Begone, Fiends!")
m.newDmg(25)
m.newTrigTag('demon')
m.newTrig('spellcast',"Exorcism")
m.newDmg(25)
m.newProc(9)
#
m = Magic("Power Leech","PL")
m.newDmg(75)
m.newTrigTag('orc')
m.newDmg(150)
m.newTrigTag('ogre')
m.newDmg(150)
m.newTrigTag('goblin')
m.newDmg(150)
m.newProc(10)
# There might be a problem with the procs on this one due to the wording
# indicating that a spell needs to be cast or owned for a single 25% dmg proc
# to trigger. I have no idea how to deal with this right now.
m = Magic("Purify","puri")
m.newDmg(100)
m.newTrigTag('demon')
m.newDmg(500)
m.newTrig('spellcast',"Mark of the Raven's Wing")
m.newDmg(25)
m.newTrig('spellcast',"Shadowstep")
m.newDmg(25)
m.newTrig('spellcast',"Inspire")
m.newDmg(25)
m.newTrig('spellowned',"Mark of the Raven's Wing")
m.newDmg(25)
m.newTrig('spellowned',"Shadowstep")
m.newDmg(25)
m.newTrig('spellowned',"Inspire")
m.newDmg(25)
m.newProc(5)
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
m = Magic("Quicken Mind","QM")
m.newDmg(0)
m.newProc(100)
# Wants pieces of Battle-Scarred set (+3). Not going to do that. (10*12)
m = Magic("Quicksand Pit","QSP")
m.newDmg(60)
m.newTrigTag('ogre')
m.newDmg(200)
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Qwil-Killer Fury","QKF")
m.newDmg(60)
m.newTrigTag('qwiladrian')
m.newDmg(150)
m.newProc(11)
#
m = Magic("Rage of the Twilight","RT")
m.newDmg(50)
m.newDmg( lambda : 2 * (OWNED['OROCTROOPS'] + OWNED['OROCGENERALS'] ) )
m.newTrigTag('demon')
m.newDmg(100)
m.newProc(10)
#
m = Magic("Raging Blizzard","RB")
m.newDmg(5)
m.newProc(100)
#
m = Magic("Raise Dead","RD")
m.newDmg(200)
m.newTrig('spellowned',"Raise Dead")
m.newDmg(100)
m.newTrigTag('demon')
m.newDmg(100)
m.newTrigTag('dragon')
m.newDmg(100)
m.newProc(10)
#   This wants you to calc for # of Spirit Raven set pieces owned. Not doing it.
m = Magic("Rally","rally")
m.newTrigTag('guild')
m.newDmg(120)
m.newTrigTag('guild')
m.newTrig('spellcast',["Unity","Deathmark","Volatile Runes"])
m.newDmg(200)
m.newProc(6)
#
m = Magic("Reflection","ref")
m.newDmg(10)
m.newProc(20)
#
m = Magic("Remove Spirit","RS")
m.newTrigTag('dragon')
m.newDmg(125)
m.newTrigTag('undead')
m.newDmg(125)
m.newProc(14)
# Wants Resurrection set pieces (+3). Not doing it. (10*12)
m = Magic("Resurrect","res")
m.newDmg(75)
m.newTrig('spellowned',"Resurrect")
m.newDmg(75)
m.newTrigTag('undead')
m.newDmg(250)
m.newProc(10)
#Proc chance increases by 10 if Blazing Sun is cast. We don't have a way to
#actually do that, so we just blend it in as a part of proc damage. Maths.
m = Magic("Sandstorm","sand")
m.newDmg(15)
m.newTrig('spellcast',"Blazing Sun")
m.newDmg(20)
m.newProc(26)
# Wants to count Battle-Scarred set (+3). Not doing it. (10*12)
m = Magic("Sap Energies","sap")
m.newDmg(60)
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
## SM changed to SaM to avoid collision with Shattered Moon
m = Magic("Savage Melodies","SaM")  
m.newTrigTag('giant')
m.newDmg(500)
m.newProc(20)
#
m = Magic("Scorched Earth","SE")
m.newDmg(100)
m.newTrig('spellcast',"Power Leech")
m.newDmg(200)
m.newTrigTag('goblin')
m.newDmg(80)
m.newTrigTag('orc')
m.newDmg(80)
m.newTrigTag('ogre')
m.newDmg(80)
m.newProc(9)
#Due to those chests from Dark Cathedral campaign, just assume that if you own
#this magic, you have all seven of those colorful generals. Cheap, but okay.
m = Magic("Seven Unyielding","7U")
m.newDmg(95)
m.newTrig('spellowned',"Seven Unyielding")
m.newDmg(7*15)
m.newProc(8)
#Shadow Strike was omitted due to same reasons as Battousai
#Shadowstep wants Shadow-Slip Assassin set. I don't. (15*9)
m = Magic("Shadowstep","SS")
m.newDmg(50)
m.newTrigTag('demon')
m.newDmg(120)
m.newProc(10)
#   This checks if Ying of the Shattered Moon is owned. We're not doing that.
m = Magic("Shattered Moon","SM")
m.newDmg(200)
m.newTrig('spellowned','Shattered Moon')
m.newDmg(100)
m.newTrigTag('human')
m.newDmg(750)
m.newProc(10)
# This wants pieces of Wee Warrior set. I say... no. (10*9)
m = Magic("Shrink","shrink")
m.newDmg(100)
m.newTrig('spellowned',"Shrink")
m.newDmg(100)
m.newTrigTag('giant')
m.newDmg(350)
m.newProc(10)
# Wants pieces of Brute Strength set. Not doing it. (5*9)
m = Magic("Siphon Strength","siphon")
m.newDmg(100)
m.newTrig('spellowned',"Siphon Strength")
m.newDmg(45)
m.newTrigTag('goblin')
m.newDmg(200)
m.newTrigTag('orc')
m.newDmg(200)
m.newTrigTag('ogre')
m.newDmg(200)
m.newProc(10)
#   This magic also checks for those gauntlet trophies. Not doing that here.
m = Magic("SMITE","SMITE")
m.setrare()
m.newDmg(500)
m.newTrig('spellowned',"SMITE")
m.newDmg(150)
m.newProc(22)
#   Checks for number of Grave Guardians owned. We don't do this.
m = Magic("Soul Pilferer","SP")
m.newTrigTag('undead')
m.newDmg(300)
m.newTrigTag('undead')
m.newTrig('spellcast',"Gravebane")
m.newDmg(400)
m.newProc(15)
# It wants pieces of the Warrior Poet set. No. (9*5)
m = Magic("Stanzas of Slaughter","SoS")
m.newDmg(120)
m.newTrig('spellcast',"Harmony")
m.newDmg(50)
m.newTrig('spellcast',"Discord")
m.newDmg(50)
m.newProc(9)
# Wants pieces of the Battle-Scarred set (+3). No. (10*12)
m = Magic("Survivor","surv")
m.newDmg(60)
m.newTrigTag('orc')
m.newDmg(200)
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
# Let's assume, due to the proliferation of those Chest of Ages things that
# if you own the magic, you have all the pieces of the Rising Dawn set.
m = Magic("Sword of Light","SoL")
m.newDmg(100)
m.newTrig('spellowned',"Sword of Light")
m.newDmg(15*9)
m.newTrigTag('dragon')
m.newDmg(150)
m.newProc(10)
# Proc chance increases by 3% on match. Goodness gracious. More math 
m = Magic("Terracles' Blessing","TB")
m.newDmg(48)
m.newTrig('spellcast',"Lyria's Swiftness")
m.newTrigTag('dragon')
m.newDmg(12)  #simulation of +3% proc rate
m.newProc(12)
#
m = Magic("Titan Killer","TK")
m.newDmg(200)
m.newTrigTag('giant')
m.newDmg(1100)
m.newDmg(lambda : 50 * OWNED['GIANTESSENCE'])
m.newProc(6)
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
m = Magic("Vampiric Aura","VA")
m.newDmg(12)
m.newProc(15)
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
# Assumes you own all six (?) pieces of Violet Knight set if you have the magic
# due to DC campaign loot
m = Magic("Violet Storm","VS")
m.newDmg(90)
m.newTrig('spellowned',"Violet Storm")
m.newDmg(5*6)
m.newProc(5)
#   This counts Depth Terror set. We're not doing that.
m = Magic("Visions of the Deep","VotD")
m.newDmg(500)
m.newTrigTag(['terror','abyssal']) #OR condition. Apply proc once.
m.newDmg(58)
m.newTrigTag('terror')
m.newTrig('spellcast',"Typhoon")
m.newDmg(28)
m.newProc(20)
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
#Omitting Web of Aeons for much the same reason as I omitted Battousai
#
m = Magic("Weightlessness","weight")
m.newDmg(100)
m.newTrig('spellowned',"Weightlessness")
m.newDmg(100)
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(10)
#
m = Magic("What's At Stake","WaS")
m.newDmg(100)
m.newTrigTag('undead')
m.newDmg(250)
m.newTrigTag('dragon')
m.newDmg(250)
m.newProc(20)
#
'''
m = Magic("Wish","wish")
m.setrare()
m.newDmg(float('NaN'))
m.newProc(float('NaN'))
'''
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
## PLATFORM-SPECIFIC MAGICS. COLLECTING THEM ALL UNDER A
## SINGLE NAME AND EXPECTING USERS TO JUST KNOW WHAT
## THESE MAGICS ARE FOR THEIR RESPECTIVE PLATFORMS
m = Magic("[LV 2500]","#1#")
m.newDmg(1000)
m.newProc(1)
#
m = Magic("[LV 5000]","#2#")
m.newDmg(1200)
m.newProc(1)
# Wants to know if you own Legend of the Demigod. I'm tempted to add it but...
# neh. Not going to.
m = Magic("[LV 10,000]","#3#")
m.newDmg(30)
m.newProc(100)
#
m = Magic("[LV 20,000]","#4#")
m.newDmg(50)
m.newDmg( lambda : math.floor(OWNED['MAGICS'] / 3) )
m.newProc(100)




if EXTRAFUNC=='selftest':
    ## Check for duplicate (fullname) entries
    allpass = True
    testpass = True
    for spell in Magic.spelllist:
        found = 0
        name1 = spell.fullname
        for spcmp in Magic.spelllist:
            if name1 == spcmp.fullname:
                found += 1
        if found>1:
            testpass = False
            print "Spell fullname duplicate found in : "+str(spell.fullname)
    if testpass:    print "No spell fullname duplicates."
    else:           allpass = False
    ## Check for nickname duplicates
    testpass = True
    for spell in Magic.spelllist:
        found = 0
        name1 = spell.nickname
        for spcmp in Magic.spelllist:
            if name1 == spcmp.nickname:
                found += 1
        if found>1:
            testpass = False
            print "Spell abbrevation duplicate found in : "+str(spell.fullname)
    if testpass:    print "No spell abbreviation duplicates."
    else:           allpass = False
    ## Check all tags in all spells if they're correctly spelled / registered
    registeredtags = ['underground','elite','deadly','worldraid','eventraid',
        'dragon','demon','aquatic','qwiladrian','winter','siege','terror',
        'insect','construct','goblin','orc','ogre','human','undead','beast',
        'magicalcreature','nightmarequeen','shadowelf','blackhand','guild',
        'festival','abyssal','beastman','plant','war','giant']
    testpass = True
    for spell in Magic.spelllist:
        for procs in spell.proclist:
            for proc in procs[1]:
                triggers = proc[1]
                if 'raidtag' in triggers:
                    for tag in triggers['raidtag']:
                        if tag not in registeredtags:
                            print "Spell "+str(spell.fullname)+" has unregistered tag: "+str(tag)
                            testpass = False
    if testpass:    print "No unregistered raid tags in spells."
    else:           allpass = False
    ## Check all spellowned/spellcast triggers against names in spell database
    testpass = True
    for spell in Magic.spelllist:
        for procs in spell.proclist:
            for proc in procs[1]:
                triggers = proc[1]
                if 'spellcast' in triggers:
                    for sname in triggers['spellcast']:
                        if not Magic.getID(sname):
                            print "Spell "+str(spell.fullname)+" has unregistered spellcast argument: "+str(sname)
                            testpass = False
                if 'spellowned' in triggers:
                    for sname in triggers['spellowned']:
                        if not Magic.getID(sname):
                            print "Spell "+str(spell.fullname)+" has unregistered spellowned argument: "+str(sname)
                            testpass = False
    if testpass:    print "No unregistered spellcast/spellowned triggers in spells."
    else:           allpass = False
    ## Check OWNED['SPELLS'] to ensure that they also appear in magic database
    testpass = True
    for sname in OWNED['SPELLS']:
        if not Magic.getID(sname):
            print "Spell name or abbreviation in OWNED['SPELLS'] not registered: "+str(sname)
            testpass = False
    if testpass:    print "No unregistered spells in OWNED['SPELLS'] list."
    else:           allpass = False
    ## ... ... ...
    ## ... ... ...
    ## ... ... ...
    if allpass:
        print "PASS: All self-test functions completed without error."
    else:
        print "FAIL: Some self-test functions have produced an error."
    sys.exit()



'''
m = Magic("","")
m.newDmg()
m.newTrig('spellcast',"")
m.newTrig('spellowned',"")
m.newTrigTag('')
m.newDmg()
m.newProc()
'''
MAIN_DIVIDER       = "============" *6
HORIZONTAL_DIVIDER = "------------" *3
print MAIN_DIVIDER
print "Raid magic, calc for tags: "+str(RAIDTAGS)
print MAIN_DIVIDER
Magic.sortMagic()
shortlist = ""
for idx,spell in enumerate(Magic.spelllist[:SLOTNUM+MAGICLIST_EXTEND]):
    print spell.fullname + ": " + str(spell.getAvg())
    shortlist += spell.nickname
    if idx == SLOTNUM-1:
        print HORIZONTAL_DIVIDER
        shortlist += ";"
    else:
        shortlist += ","
print MAIN_DIVIDER
print "Short list: " + str(shortlist[:-1])
print MAIN_DIVIDER










