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
MAGICLIST_EXTEND = 3

OWNED = {
    'MOUNTS':400,
    'LEGIONS':100,
    'TROOPS':200,
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
    'DRAGONESSENCE':10,
    'DRAGONMOUNTS':20,
    "KATH'IN":False,   #For Fury of the Deep, since owning this gen affects it greatly.
    'SCULPTEDCRYSTAL':0,
    'HARVESTEDCRYSTAL':0,
    
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
        
    @classmethod
    def sortMagic(cls):
        global SLOTNUM,EXTRAFUNC
        if EXTRAFUNC == "pessimal": sortdir = False
        else:                       sortdir = True
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
        global RAIDTAGS,OWNED,USERAREMAGIC,SHOWDEBUG,SLOTNUM
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
Magic("NULL_ENTRY","NULL_ENTRY")
#
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
#Omitting Battousai. It has a raid condition we can't quantify without
#requiring annoying extra inputs.
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
#Counts amounts of individual mounts owned. My god. No. Just assume we have
#the maximal amount and call it a day.
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
#   This magic checks for those gauntlet trophies. Not doing that here.
m = Magic("Blessing of Mathala","BoM")
m.setrare()
m.newDmg(850)
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
#   Wants to check for three different generals. No way.
m = Magic("Blood Moon","BM")
m.newDmg(100)
m.newTrig('spellowned',"Glimmering Moon")
m.newDmg(50)
m.newTrigTag('human')
m.newDmg(100)
m.newProc(10)
#   Checks if five particular generals are owned. No way we're doing that.
m = Magic("Boil","boil")
m.newDmg(50)
m.newTrigTag('aquatic')
m.newDmg(250)
m.newProc(11)
#   Checks for Battle-Scarred set and others. Wow. No. Not just no, but hell no.
m = Magic("Bramblewire Trap","BT")
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
#Omitting Brough's Trick for same reason as Battousai
#
m = Magic("Burning Rain","BR")
m.newDmg(3)
m.newProc(100)
#
m = Magic("Buster 2.0","B2")
m.newDmg(10000000000)
m.newProc(0) # ...
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
#   Checks for Incinerated Soldiers owned. We aren't doing that here.
m = Magic("Conflagration","conf")
m.newTrigTag('winter')
m.newDmg(100)
m.newTrigTag('winter')
m.newTrig('spellowned','Living Flame')
m.newDmg(100)
m.newTrigTag('winter')
m.newTrig('spellcast','Flame Serpent')
m.newDmg(150)
m.newProc(25)
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
# This magic wants to count pieces of Acidic Armor set, including a bunch of
# things one wouldn't consider as part of a set. Sure as hell not doing that.
m = Magic("Corrode","corr")
m.newDmg(75)
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
#   This wants number of Curious Cuirassier pieces. I won't do it.
m = Magic("Desiccate","desi")
m.newDmg(50)
m.newDmg( lambda : 5 * OWNED['PLANTESSENCE'] )
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
#   This spell wants to know if you own Wish Warriors or Arch Djinn's Lamp.
#   Not going to bother with that at this time, even if the damage could add up
m = Magic("Djinnpocalypse","Dj")
m.newDmg(1000)
m.newTrigTag('magicalcreature')
m.newDmg(150)
m.newProc(10)
# If you have Doorway, it's VERY hard to not have all 9 pieces of Veil-Walker
# set. Assume magic ownership equals set ownership. This magic also has a
# Haste effect, which is a whole kettle of beans we aren't touching. Ever.
m = Magic("Doorway","door")
m.newDmg(50)
m.newTrig('spellowned',"Doorway")
m.newDmg(9*5)
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
# Wants Dune Stalker set. Not giving it the time of day. Go do it yourself.
m = Magic("Dune Tears","DT")
m.newDmg(75)
m.newTrigTag('elite')
m.newDmg(200)
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
#   Checks for ownership of Monster Fisherman and Fish Hooks. Not doing that.
#   Since its damage is so significant, we'll do the cheap way out and simply
#   check if you own the magic. If you own it, you'll likely own the others.
m = Magic("Enraged Feeding Frenzy","EFF")
m.newDmg(50)
m.newTrig('spellowned',"Enraged Feeding Frenzy")
m.newDmg(100+30*5)
m.newTrigTag('aquatic')
m.newDmg(300)
m.newProc(10)
#Checks if Iliad the Recorder, Panoptica, and the other Panoptical are owned.
#Cheating a bit and assuming you own them if you own this magic too.
m = Magic("Eternal Sight","ES")
m.newDmg(20)
m.newTrig('spellowned',"Eternal Sight")
m.newDmg(5*3)
m.newProc(100)
# Somewhat simplified proc.
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
# Wants to know if you own a bunch of generals. Due it now being f2p release,
# we can assume you own them all if you have this magic. Cheap? Yeah.
# I won't clutter my OWNED dict with stuff like that.
m = Magic("Fatal Aim","FaA")
m.newDmg(200)
m.newTrig('spellowned',"Fatal Aim")
m.newDmg(50*3)
m.newTrigTag('goblin')
m.newDmg(80)
m.newTrigTag('orc')
m.newDmg(90)
m.newTrigTag('ogre')
m.newDmg(100)
m.newProc(9)
# Almost all the damage comes from owning three particular generals.
# Ew. No. I won't allow it. Nope. This spell will never get a ranking from me.
m = Magic("Fearless Advance","FeA")
m.newDmg(100)
m.newProc(10)
#   Checks for ownership of Monster Fisherman and Fish Hooks. Not doing that.
#   Since its damage is so significant, we'll do the cheap way out and simply
#   check if you own the magic. If you own it, you'll likely own the others.
m = Magic("Feeding Frenzy","FF")
m.newDmg(50)
m.newTrig('spellowned',"Feeding Frenzy")
m.newDmg(50+25*5)
m.newTrigTag('aquatic')
m.newDmg(100)
m.newProc(9)
#   This checks for Kindly Folk set. We're not going to do that.
m = Magic("Fey Flame","fey")
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
m = Magic("Fireworks","fire")
m.newDmg(75)
m.newTrig('spellowned',"")
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
# Wants to count Hobby Horses. No.
m = Magic("Free Will","FW")
m.newDmg(100)
m.newTrig('spellowned',"Free Will")
m.newDmg(100)
m.newTrigTag('winter')
m.newDmg(200)
m.newTrigTag('siege')
m.newDmg(200)
m.newProc(10)
#This wants Iirhinian Arrow Master set pieces. No. Not doing it.
m = Magic("From Iirhine With Love","FIWL")
m.newDmg(210)
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
#   This one is complicated. Did some preprocessing to make it fit our paradigm
m = Magic("Guster's Fault","GF")
m.newDmg(190)
m.newProc(20)
#
m = Magic("Guzzlebeard's Special Reserve","GSR")
m.newDmg(100)
m.newDmg(lambda : 5 * (OWNED['DWARFTROOPS'] + OWNED['DWARFGENERALS']) )
m.newTrigTag('underground')
m.newDmg(400)
m.newTrig('spellcast','A Light in the Darkness')
m.newDmg(300)
m.newProc(10)
# There's a lot of bonuses for owning a lot of different sets. Like, almost 
# half the damage. I'm not calculating that here. (25,35,40,50)
m = Magic("Hailstorm","hail")
m.newDmg(50)
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
# Wants you to have whole endless dawn set. Due to recent f2p stuff, you'll
# probably own all pieces of that set if you have this magic. Cheaping out.
m = Magic("Hemorrhage","hemo")
m.newDmg(200)
m.newTrig('spellowned',"Hemorrhage")
m.newDmg(10*9)
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
# Simplified. The spell's name is rather apt.
m = Magic("Insanity Laughs","IL")
m.newDmg(0.15 * 1500)
m.newProc(5)
#Wants to know if you own Sir Lenus. I don't want to check that :sadfaic:
m = Magic("Inspire","insp")
m.newDmg(125)
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
m = Magic("Magic Torch","torch") ## haha
m.newDmg(0)
m.newProc(0)
#
m = Magic("Manifest Dread","MD")
m.newDmg()
m.newTrig('spellcast',"")
m.newTrig('spellowned',"")
m.newTrigTag('')
m.newDmg()
m.newProc()










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
m = Magic("Noxious Breath","NB")
m.newDmg(400)
m.newTrigTag(['human','beastman']) #OR CONDITION
m.newDmg(140)
m.newProc(20)
#
m = Magic("Pestilent Bolt","PB")
m.newDmg(550)
m.newTrigTag(['orc','ogre','goblin']) #OR CONDITION
m.newTrig('spellcast',"Pestilent Bolt")
m.newDmg(170)
m.newProc(15)
#
m = Magic("Poison","P")
m.newDmg(4)
m.newProc(7)
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
#   This wants you to calc for # of Spirit Raven set pieces owned. Not doing it.
m = Magic("Rally","rally")
m.newTrigTag('guild')
m.newDmg(120)
m.newTrig('spellcast',["Unity","Deathmark","Volatile Runes"])
m.newDmg(200)
m.newProc(6)
## SM changed to SaM to avoid collision with Shattered Moon
m = Magic("Savage Melodies","SaM")  
m.newTrigTag('giant')
m.newDmg(500)
m.newProc(20)
#   This checks if Ying of the Shattered Moon is owned. We're not doing that.
m = Magic("Shattered Moon","SM")
m.newDmg(200)
m.newTrig('spellowned','Shattered Moon')
m.newDmg(100)
m.newTrigTag('human')
m.newDmg(750)
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
m = Magic("Veil Dust","VD")
m.newDmg(300)
m.newTrig('spellowned',"Veil Dust")
m.newDmg(50)
m.newTrig('spellowned',"Fey Flame")
m.newDmg(50)
m.newTrigTag('magicalcreature')
m.newDmg(400)
m.newProc(10)
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










