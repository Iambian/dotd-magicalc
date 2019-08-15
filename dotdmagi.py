''' Best Magic Calculator for Dawn of the Dragons
    usage: dotdmagi.py numsspellslots tag1 [tag2 [tag3...]]
    returns: Details of best magics from best to worst and a short string to
             paste on raids regarding which magics should be used
             
    NOTE: Tags may not contain any spaces. e.g. "Black Hand" becomes "blackhand"
    NOTE: IF YOU ARE NEW TO PYTHON, ALL LABELS, NAMES, AND TEXT IS
          CASE-SENSITIVE. RESPECT IT, OR YOU WILL HAVE A bad time.
'''

''' Programmer's note: This was supposed to be simple. How did it get this messy? '''

import sys,os,copy,math,time,datetime

try:
    SLOTNUM = int(sys.argv[1])
    EXTRAFUNC = False
except:
    SLOTNUM = 0
    EXTRAFUNC = sys.argv[1]
def checkDel(s):
    global RAIDTAGS
    if s in RAIDTAGS:   return RAIDTAGS.remove(s) or True
    else:               return False
    
SHOWDEBUG = False
DEBUGDOUBLES = False
SPELLSPLITDEBUG = False
RAIDTAGS = [s.lower() for s in sys.argv[2:]]
MAGICLIST = []
MAGICLIST_EXTEND = 3
AVGMODE = 'avg'

## ==========================================================================
##   This is the profile you want to edit if you want to change the default 
## ==========================================================================
OWNED = {
    'MOUNTS':432,
    'LEGIONS':400,
    'TROOPS':800,
    'GENERALS':400,
    ## number of magics owned. This value holds priority over length of SPELLS
    'MAGICS':118,
    ## SPELLS shows exactly what magics you own.
    'SPELLS':["AF","anni","ava","beach","BF","BD","BL","boil","BB","BR","CD","cata","CE","CKi","conf","cont","CEx",
        "CP","DF","DS","DE","DM","deep","dehum","disc","disi","dism","Dj","door","dup","elec","EFF","ES","exo","EitD","FaA",
        "fire","FS","FotD","GG","GB","GID","GMT","GF","GSR","hail","harm","HC","HvK","HK","hemo","hib","HSE","HN","howl",
        "IS","ID","IB","IL","insp","int","intox","IG","LID","LP","lev","LR","LD","MID","melt","MT","MTS","MS",
        "NK","NM","NB","OB","PB","PoL","P","pos","PL","puri","PS","QM","QKF","RD","rally","RS","res","SaM","SE","7U","SS","SM",
        "siphon","SP","SoL","TK","TotH","typh","uni","VA","VS","VR","VE","weight","WaS","WV","#1#","#2#","#3#"
    ],
    'GIANTESSENCE':9,
    'BEASTMANESSENCE':22,
    'FESTIVALESSENCE':11,
    'UNDERGROUNDESSENCE':35,
    'PLANTESSENCE':7,
    'DWARFTROOPS':45,
    'DWARFGENERALS':33,
    'MAGICALBEINGTROOPS':62,
    'MAGICALBEINGGENERALS':31,
    'OROCTROOPS':34,
    'OROCGENERALS':20,
    'DRAGONESSENCE':40,
    'DRAGONMOUNTS':49,
    "KATH'IN":False,   #For Fury of the Deep, since owning this gen affects it greatly.
    'SCULPTEDCRYSTAL':100,
    'HARVESTEDCRYSTAL':500,
    ##
    'AUREATE_TROPHY':False,    #For gauntlet
    'ARGENT_TROPHY':False,
    'BRONZED_TROPHY':True,
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
    'GEN_BURUT_THE_HUNGRY':False,  #For Consume. Part of many things.
    'ITM_TURKEY_OF_PLENTY':2,    #Up to 5
    'ITM_DEER_OF_PLENTY':2,      #Up to 5
    'ITM_BEAR_OF_PLENTY':2,      #Up to 5
    'ITM_BOAR_OF_PLENTY':5,      #Up to 5
    'SET_ACIDIC_ARMOR':0,        #9 for set, +7 for other stuff wanted by Corrode
    'GEN_HAIMISH':True,          #The following gens and 3 items for Deep Freeze
    'GEN_OLD_DEAD_ELVIGAR':True,
    'GEN_UTHIN':True,
    'GEN_VILI':True,
    'ITM_CRYSTAL_OF_THE_DEADLY_COLD':True,
    'ITM_KINGSJAW':True,
    'ITM_DARKES_SIGHT':True,
    'SET_CURIOUS_CUIRASSIER':0,  #9 for set.
    'TRP_WISH_WARRIOR':0,        #Up to 50
    'ARM_ARCH_DJINNS_LAMP':False,
    'SET_VEIL_WALKER':0,         #9 for set !!! Expected to have if own Doorway
    'SET_DUNE_STALKER':0,        #9 for set
    'GEN_MONSTER_FISHERMAN':True,
    'ITM_FISH_HOOK':6,           #Up to 6 (for now). For (Enraged) Feeding Frenzy
    'GEN_ILIAD_THE_RECORDER':True,  #For Eternal Sight
    'GEN_PANOPTICA':True,
    'GEN_PANOPTICA_THE_OMNISCIENT_ANGEL':True,
    'GEN_BEIJA_THE_ERUDITE':True, #For Fatal Aim
    'GEN_ESTREL_THE_JUST':True,
    'GEN_HAWKER_THE_GENTEEL':True,
    'GEN_GARKURA_THE_DREADNAUGHT':False, #For Fearless Advance
    'GEN_ABIGAIL_PIETRI_PHINEAS':False,
    'SET_KINDLY_FOLK':0,         #10 for set
    'ITM_HOBBY_HORSE':0,         #Up to 10
    'SET_IIRHINIAN_ARROW_MASTER':0, #9 for set
    'SET_SNOW_WARRIOR':9,        #9 for set
    'SET_SNOW_WARLORD':9,        #9 for set
    'SET_SLEET_WARRIOR':9,       #9 for set
    'SET_SNOW_FOX':0,            #9 for set
    'SET_ENDLESS_DAWN':9,        #9 for set
    'TRP_SIR_LENUS':False,       #For Inspire
    'SET_JOVIAL_JESTER':0,       #9 for set
    'SET_CELEBRATION':0,         #9 for set
    'SET_FOREST_SENTINEL':9,     #9 for set
    'ARM_SABIRAHS_ASHES':False,  #For Judgement
    'ARM_CERMARINAS_BLADE':False,
    'ITM_STORMSHIP':50,          #up to 50
    'TRP_CLOUD_ELEMENTAL':25,    #up to 25
    'GEN_PASITHEA':False,
    'GEN_BELLEFOREST':False,
    'GEN_ESCH':False,
    'TRP_SLEEPLESS_SOLDIERS':50,  #Up to 50. You probably own them all already.
    'TRP_GRIFFIN_CHAMPIONS':0,    #Up to 100
    'SET_INFINITE_DAWN':0,        #10 for set
    'GEN_SIR_JORIM':False,        #For Mystic Slaughterers
    'SET_SPIRIT_RAVEN':9,         #9 for set. For Rally
    'SET_RESURRECTION':0,         #9 for set +3 more as Resurrect wants
    'GEN_SAR_VELANIA_THE_RED':True, #For Seven Unyielding. Yeah. THAT magic.
    'GEN_SIR_BOHEMOND_THE_ORANGE':True,
    'GEN_SIR_EMERIC_THE_YELLOW':True,
    'GEN_SIR_AARON_THE_BLUE':True,
    'GEN_SIR_COLBAEUS_THE_GREEN':True,
    'GEN_SAR_MEURA_THE_INDIGO':True,
    'GEN_SAR_WENNI_THE_VIOLET':True,
    'SET_SHADOW-SLIP_ASSASSIN':0, #9 for set
    'GEN_YING_OF_THE_SHATTERED_MOON':True, #For Shattered Moon
    'SET_WEE_WARRIOR':0,          #9 for set
    'SET_BRUTE_STRENGTH':0,       #9 for set
    'TRP_GRAVE_GUARDIAN':0,       #Up to 50
    'SET_WARRIOR_POET':0,         #9 for set
    'SET_RISING_DAWN':0,          #10 for set
    'SET_VIOLET_KNIGHT':0,        #9 for set
    'SET_DEPTH_TERROR':0,         #10 for set
    'ITM_LEGEND_OF_THE_DEMIGOD':True, #For lv10k magic
}




if checkDel('raremagic=true'):  USERAREMAGIC = True
else:                           USERAREMAGIC = False
if checkDel('avgmode=max'): AVGMODE = 'max'
else:                       AVGMODE = 'avg'

if checkDel('profile=maxed') or checkDel('profile=whale') or checkDel('profile=wailord'):
    OWNED = {
        'MOUNTS':432,
        'LEGIONS':482,
        'TROOPS':860,
        'GENERALS':652,
        ## number of magics owned. This value holds priority over length of SPELLS
        'MAGICS':187,
        ## SPELLS shows exactly what magics you own.
        'SPELLS':["LitD","AF","anni","AM","AD","ava","beach","BF","BD","BS","BoM","BL","BM","boil","BT","BB","BR","CD","cata","CE","CKi","CC","conf","cons","cont","CEx","corr",
            "CP","CoS","DF","DS","DE","DM","deep","dehum","desi","DD","disc","disi","dism","Dj","door","DB","DT","dup","elec","EFF","ES","exo","EW","EitD","FaF","FaA",
            "FeA","FF","fey","fire","FS","FW","FIWL","FotD","GG","GM","GB","GID","GMT","GP","GuB","GF","GSR","hail","harm","HC","HvK","HK","hemo","hib","HSE","HN","howl",
            "IS","ID","IB","IL","insp","int","intox","IG","judge","KG","KN","LID","LP","lev","LR","LD","LS","MD","MV","MG","MID","MRW","MoM","mel","melt","MT","MTS","MS",
            "NK","NM","NB","OB","PB","PoL","P","pos","PL","puri","PS","QM","QSP","QKF","RT","RB","RD","rally","ref","RS","res","sand","sap","SaM","SE","7U","SS","SM",
            "shrink","siphon","SMITE","SP","SoS","surv","SoL","TB","TK","TotH","typh","uni","VA","VD","VS","VotD","VR","VE","weight","WaS","WV","#1#","#2#","#3#","#4#"
        ],
        'GIANTESSENCE':9,
        'BEASTMANESSENCE':22,
        'FESTIVALESSENCE':11,
        'UNDERGROUNDESSENCE':35,
        'PLANTESSENCE':7,
        'DWARFTROOPS':45,
        'DWARFGENERALS':33,
        'MAGICALBEINGTROOPS':62,
        'MAGICALBEINGGENERALS':31,
        'OROCTROOPS':34,
        'OROCGENERALS':20,
        'DRAGONESSENCE':40,
        'DRAGONMOUNTS':49,
        "KATH'IN":True,   #For Fury of the Deep, since owning this gen affects it greatly.
        'SCULPTEDCRYSTAL':156,
        'HARVESTEDCRYSTAL':667,
        ##
        'AUREATE_TROPHY':True,    #For gauntlet
        'ARGENT_TROPHY':True,
        'BRONZED_TROPHY':True,
        'GEN_SMILING_SARAH':True, #For Blood Moon
        'GEN_ZURK':True,
        'GEN_KOLEMALU':True,
        'GEN_RANINA':True,        #For Boil
        'GEN_LAOCONS_GHOST':True,
        'GEN_LORD_VERNE':True,
        'GEN_CAPTAIN_TIPHANTES':True,
        'GEN_FIRST_MATE_BRAEUS':True,
        'SET_BATTLE_SCARRED':9,      #9 for set, +3 for other stuff that the spells want
        'ARM_LIVING_FLAME':True,
        'TRP_INCINERATED_SOLDIER':50, #Up to 50
        'GEN_BURUT_THE_HUNGRY':True,  #For Consume. Part of many things.
        'ITM_TURKEY_OF_PLENTY':5,    #Up to 5
        'ITM_DEER_OF_PLENTY':5,      #Up to 5
        'ITM_BEAR_OF_PLENTY':5,      #Up to 5
        'ITM_BOAR_OF_PLENTY':5,      #Up to 5
        'SET_ACIDIC_ARMOR':16,        #9 for set, +7 for other stuff wanted by Corrode
        'GEN_HAIMISH':True,         #The following gens and 3 items for Deep Freeze
        'GEN_OLD_DEAD_ELVIGAR':True,
        'GEN_UTHIN':True,
        'GEN_VILI':True,
        'ITM_CRYSTAL_OF_THE_DEADLY_COLD':True,
        'ITM_KINGSJAW':True,
        'ITM_DARKES_SIGHT':True,
        'SET_CURIOUS_CUIRASSIER':9,  #9 for set.
        'TRP_WISH_WARRIOR':50,        #Up to 50
        'ARM_ARCH_DJINNS_LAMP':True,
        'SET_VEIL_WALKER':9,         #9 for set !!! Expected to have if own Doorway
        'SET_DUNE_STALKER':9,        #9 for set
        'GEN_MONSTER_FISHERMAN':True,
        'ITM_FISH_HOOK':6,           #Up to 6 (for now). For (Enraged) Feeding Frenzy
        'GEN_ILIAD_THE_RECORDER':True,  #For Eternal Sight
        'GEN_PANOPTICA':True,
        'GEN_PANOPTICA_THE_OMNISCIENT_ANGEL':True,
        'GEN_BEIJA_THE_ERUDITE':True, #For Fatal Aim
        'GEN_ESTREL_THE_JUST':True,
        'GEN_HAWKER_THE_GENTEEL':True,
        'GEN_GARKURA_THE_DREADNAUGHT':True, #For Fearless Advance
        'GEN_ABIGAIL_PIETRI_PHINEAS':True,
        'SET_KINDLY_FOLK':10,        #10 for set
        'ITM_HOBBY_HORSE':10,        #Up to 10
        'SET_IIRHINIAN_ARROW_MASTER':9, #9 for set
        'SET_SNOW_WARRIOR':9,        #9 for set
        'SET_SNOW_WARLORD':9,        #9 for set
        'SET_SLEET_WARRIOR':9,       #9 for set
        'SET_SNOW_FOX':9,            #9 for set
        'SET_ENDLESS_DAWN':9,        #9 for set
        'TRP_SIR_LENUS':True,       #For Inspire
        'SET_JOVIAL_JESTER':9,       #9 for set
        'SET_CELEBRATION':9,         #9 for set
        'SET_FOREST_SENTINEL':9,     #9 for set
        'ARM_SABIRAHS_ASHES':True,  #For Judgement
        'ARM_CERMARINAS_BLADE':True,
        'ITM_STORMSHIP':50,          #up to 50
        'TRP_CLOUD_ELEMENTAL':25,     #up to 25
        'GEN_PASITHEA':True,
        'GEN_BELLEFOREST':True,
        'GEN_ESCH':True,
        'TRP_SLEEPLESS_SOLDIERS':50,  #Up to 50. You probably own them all already.
        'TRP_GRIFFIN_CHAMPIONS':100,  #Up to 100
        'SET_INFINITE_DAWN':10,       #10 for set
        'GEN_SIR_JORIM':True,         #For Mystic Slaughterers
        'SET_SPIRIT_RAVEN':9,         #9 for set. For Rally
        'SET_RESURRECTION':12,        #9 for set +3 more as Resurrect wants
        'GEN_SAR_VELANIA_THE_RED':True, #For Seven Unyielding. Yeah. THAT magic.
        'GEN_SIR_BOHEMOND_THE_ORANGE':True,
        'GEN_SIR_EMERIC_THE_YELLOW':True,
        'GEN_SIR_AARON_THE_BLUE':True,
        'GEN_SIR_COLBAEUS_THE_GREEN':True,
        'GEN_SAR_MEURA_THE_INDIGO':True,
        'GEN_SAR_WENNI_THE_VIOLET':True,
        'SET_SHADOW-SLIP_ASSASSIN':0, #9 for set
        'GEN_YING_OF_THE_SHATTERED_MOON':True, #For Shattered Moon
        'SET_WEE_WARRIOR':9,          #9 for set
        'SET_BRUTE_STRENGTH':9,       #9 for set
        'TRP_GRAVE_GUARDIAN':50,      #Up to 50
        'SET_WARRIOR_POET':9,         #9 for set
        'SET_RISING_DAWN':10,         #10 for set
        'SET_VIOLET_KNIGHT':9,        #9 for set
        'SET_DEPTH_TERROR':10,        #10 for set
        'ITM_LEGEND_OF_THE_DEMIGOD':True, #For lv10k magic
        }
    pass
    
elif checkDel('profile=alt'):
    OWNED = {
        'MOUNTS':50,
        'LEGIONS':50,
        'TROOPS':50,
        'GENERALS':50,
        ## number of magics owned. This value holds priority over length of SPELLS
        'MAGICS':15,
        ## SPELLS shows exactly what magics you own.
        'SPELLS':["BB","dehum","disc","elec","GID","GMT","HC",
            "ID","LID","LP","MT","MTS","NK","P","QM","VR","weight"
        ],
        'GIANTESSENCE':1,
        'BEASTMANESSENCE':13,
        'FESTIVALESSENCE':0,
        'UNDERGROUNDESSENCE':18,
        'PLANTESSENCE':0,
        'DWARFTROOPS':5,
        'DWARFGENERALS':5,
        'MAGICALBEINGTROOPS':5,
        'MAGICALBEINGGENERALS':5,
        'OROCTROOPS':5,
        'OROCGENERALS':5,
        'DRAGONESSENCE':10,
        'DRAGONMOUNTS':5,
        "KATH'IN":False,   #For Fury of the Deep, since owning this gen affects it greatly.
        'SCULPTEDCRYSTAL':0,
        'HARVESTEDCRYSTAL':0,
        ##
        'AUREATE_TROPHY':False,    #For gauntlet
        'ARGENT_TROPHY':False,
        'BRONZED_TROPHY':True,
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
        'GEN_BURUT_THE_HUNGRY':False,  #For Consume. Part of many things.
        'ITM_TURKEY_OF_PLENTY':0,    #Up to 5
        'ITM_DEER_OF_PLENTY':0,      #Up to 5
        'ITM_BEAR_OF_PLENTY':0,      #Up to 5
        'ITM_BOAR_OF_PLENTY':0,      #Up to 5
        'SET_ACIDIC_ARMOR':0,        #9 for set, +7 for other stuff wanted by Corrode
        'GEN_HAIMISH':False,          #The following gens and 3 items for Deep Freeze
        'GEN_OLD_DEAD_ELVIGAR':False,
        'GEN_UTHIN':False,
        'GEN_VILI':False,
        'ITM_CRYSTAL_OF_THE_DEADLY_COLD':False,
        'ITM_KINGSJAW':False,
        'ITM_DARKES_SIGHT':False,
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
        'SET_JOVIAL_JESTER':0,       #9 for set
        'SET_CELEBRATION':0,         #9 for set
        'SET_FOREST_SENTINEL':0,     #9 for set
        'ARM_SABIRAHS_ASHES':False,  #For Judgement
        'ARM_CERMARINAS_BLADE':False,
        'ITM_STORMSHIP':0,          #up to 50
        'TRP_CLOUD_ELEMENTAL':0,    #up to 25
        'GEN_PASITHEA':False,
        'GEN_BELLEFOREST':False,
        'GEN_ESCH':False,
        'TRP_SLEEPLESS_SOLDIERS':0,  #Up to 50. You probably own them all already.
        'TRP_GRIFFIN_CHAMPIONS':0,    #Up to 100
        'SET_INFINITE_DAWN':0,        #10 for set
        'GEN_SIR_JORIM':False,        #For Mystic Slaughterers
        'SET_SPIRIT_RAVEN':0,         #9 for set. For Rally
        'SET_RESURRECTION':0,         #9 for set +3 more as Resurrect wants
        'GEN_SAR_VELANIA_THE_RED':False, #For Seven Unyielding. Yeah. THAT magic.
        'GEN_SIR_BOHEMOND_THE_ORANGE':False,
        'GEN_SIR_EMERIC_THE_YELLOW':False,
        'GEN_SIR_AARON_THE_BLUE':False,
        'GEN_SIR_COLBAEUS_THE_GREEN':False,
        'GEN_SAR_MEURA_THE_INDIGO':False,
        'GEN_SAR_WENNI_THE_VIOLET':False,
        'SET_SHADOW-SLIP_ASSASSIN':0, #9 for set
        'GEN_YING_OF_THE_SHATTERED_MOON':False, #For Shattered Moon
        'SET_WEE_WARRIOR':0,          #9 for set
        'SET_BRUTE_STRENGTH':0,       #9 for set
        'TRP_GRAVE_GUARDIAN':0,       #Up to 50
        'SET_WARRIOR_POET':0,         #9 for set
        'SET_RISING_DAWN':0,          #10 for set
        'SET_VIOLET_KNIGHT':0,        #9 for set
        'SET_DEPTH_TERROR':0,         #10 for set
        'ITM_LEGEND_OF_THE_DEMIGOD':False, #For lv10k magic
    }
    
else:
    pass
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
        self.reset()
        self.fullname = fullname
        self.nickname = nickname
        self.numspells = 1
        self.contains = [self]
        self.month = 12
        self.id = Magic.magic_id
        Magic.magic_id += 1
        Magic.spelllist.append(self)
        
    def reset(self):
        self.proclist = []  #list of 2-lists of [procrate,[listofprocs]]
        self.curproc = list()   #proc entry [procDamage, {triggercond:triggerdata,...}]
        self.temptrigger = dict()
        self.israre = False
        self.avgfound = 0
        
    def __lt__(self,other):
        return self.avgfound < other.avgfound 
    def __eq__(self,other):
        if isinstance(other,Magic): other = other.id
        if isinstance(self,Magic):  self =  self.id
        return self == other
    def __hash__(self):
        return self.id

    def __repr__(self):
        return "[Magic: ("+str(self.id)+") "+str(self.fullname)+"]"
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
    
        
    @staticmethod
    def getSpell(spellid):
        for i in Magic.spelllist:
            if i.id == spellid:
                return i
        return Magic.spelllist[0]
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
        if isinstance(spell,str) and not isinstance(EXTRAFUNC,str):
            spell = magic.fromtimestamp(time.time())
            spell = [spell.day == EXTRAFUNC+1,spell] #Sort num vs object
        else:
            if isinstance(spell,str): spell = Magic.getID(spell)
            if isinstance(spell,int): spell = Magic.getSpell(spell)
            spell = [spell,spell.contains[0]]
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
        # Initial sorting
        Magic.collateAverage(0)
        Magic.spelllist.sort(reverse=sortdir)
        Magic.collateAverage(SLOTNUM + MAGICLIST_EXTEND)
        Magic.spelllist.sort(reverse=sortdir)
        #return
        
        #Iterate until there are no more spells to break apart
        cls.stickyspells = []
        while (cls.spellBreakApart()): pass
        cls.stickyspells = list(set(cls.stickyspells))  #remove duplicates
        #Remove all remaining multispells
        #'''
        for spell in Magic.spelllist[:]:
            if spell.numspells > 1:
                Magic.spelllist.remove(spell)
        #'''
        #Move stickies to the end of the list
        #print [s.fullname for s in cls.stickyspells]
        for sticky in cls.stickyspells:
            #print sticky.fullname
            if sticky in Magic.spelllist:
                Magic.spelllist.remove(sticky)
            Magic.spelllist.insert(0,sticky)
        cls.stickyspells = Magic.spelllist[:SLOTNUM]
        cls.stickyspells.sort(reverse=sortdir)
        Magic.spelllist = Magic.stickyspells + Magic.spelllist[SLOTNUM:]
        
        #Resort
        '''
        Magic.collateAverage(SLOTNUM)
        Magic.spelllist.sort(reverse=sortdir)
        '''
        
        
    @classmethod
    def spellBreakApart(cls):
        global SPELLSPLITDEBUG
        self = Magic.getSpell(1)  #using this for access to Magic.spelllist
        spellbroken = False
        for idx,spell in enumerate(cls.spelllist[:SLOTNUM]):
            if (SPELLSPLITDEBUG): print "Spell check: "+str(spell.fullname)
            if spell.numspells == 2:
                spellbroken = True
                if (SPELLSPLITDEBUG): print "Double spell breakdown"
                spell_A = spell.contains[0]
                spell_B = spell.contains[1]
                #Case 2: both magics are individually in list.
                #Action: Remove the pair
                if set(spell.contains).issubset(set(cls.spelllist[:SLOTNUM])):
                    if (SPELLSPLITDEBUG): print "Both spells found"
                    cls.spelllist.remove(spell)
                #Case 1: One of the magics is in the list.
                #Action: Complicated. Involves hidden class shenanigans
                elif (set(spell.contains) & set(cls.spelllist[:SLOTNUM])):
                    if spell_A in cls.spelllist[:SLOTNUM]:
                        if (SPELLSPLITDEBUG):
                            print "Spell A found"
                            print spell.getAvgSub(spell_B)
                            print self.getAvgSub(spell_A)
                            print spell.getAvgSub(spell_A)
                        t = spell.getAvgSub(spell_B) + (self.getAvgSub(spell_A) - spell.getAvgSub(spell_A))
                        if t > cls.spelllist[:SLOTNUM][-1].getAvg():
                            if (SPELLSPLITDEBUG): print "Spell B stickied"
                            cls.stickyspells.append(spell_B)
                            cls.spelllist.remove(spell)
                        else:
                            if (SPELLSPLITDEBUG): print "Spell B didn't make it..."
                            cls.spelllist.remove(spell)
                    elif spell_B in cls.spelllist[:SLOTNUM]:
                        if (SPELLSPLITDEBUG): 
                            print "Spell B found"
                            print spell.getAvgSub(spell_A)
                            print self.getAvgSub(spell_B)
                            print spell.getAvgSub(spell_B)
                        t = spell.getAvgSub(spell_A) + (self.getAvgSub(spell_B) - spell.getAvgSub(spell_B))
                        if t > cls.spelllist[:SLOTNUM][-1].getAvg():
                            if (SPELLSPLITDEBUG): print "Spell A stickied"
                            cls.spelllist.append(spell_A)
                            cls.spelllist.remove(spell)
                        else:
                            if (SPELLSPLITDEBUG): print "Spell A didn't make it..."
                            cls.spelllist.remove(spell)
                    else: sys.exit("Assert failure: Partial list exists in main")
                #Case 0: None of the magics is in the list
                #Action: Pop both single magic then shuffle to top. Remove pair.
                else:
                    if (SPELLSPLITDEBUG): print "None of the pair found"
                    newspell_A = cls.spelllist.pop(cls.spelllist.index(spell_A))
                    newspell_B = cls.spelllist.pop(cls.spelllist.index(spell_B))
                    cls.stickyspells.append(newspell_A)
                    cls.stickyspells.append(newspell_B)
                    cls.spelllist.remove(spell)
        return spellbroken
        
        
    @staticmethod
    def getID(name_or_nick):
        for spell in Magic.spelllist:
            if name_or_nick == spell.fullname or name_or_nick == spell.nickname:
                return spell.id
        return 0
        
    def getAvg(self):
        global EXTRAFUNC,AVGMODE
        averages = []
        for spell in self.contains:
            averages.append(self.getAvgSub(spell))
        if AVGMODE=='avg':
            return sum(averages)/len(averages)
        elif AVGMODE=='max':
            return max(averages)
        else:
            return float('inf') if EXTRAFUNC=='pessimal' else 0
        
    def getAvgSub(self,spell):
        global RAIDTAGS,OWNED,USERAREMAGIC,SHOWDEBUG,SLOTNUM,EXTRAFUNC,AVGMODE
        #self = spell     #make it so each spell instance is usable
        if isinstance(spell,str):   spell = self.getID(spell)
        if isinstance(spell,int):   spell = self.getSpell(spell)
        curproctotal = 0
        maxproc = 0
        if spell.israre and not USERAREMAGIC:
            return float('inf') if EXTRAFUNC == 'pessimal' else 0
        #print "Proclist: "+str(self.proclist)
        if SHOWDEBUG: print "-----------------------"
        for procs in spell.proclist:
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
                    for magic in self.spelllist[:SLOTNUM]:
                        data = triggers['spellcast']
                        #convert spell names into IDs to membership test against
                        for i in range(len(data)):
                            if isinstance(data[i],str):
                                data[i] = self.getID(data[i])
                        if magic.id in data:
                            triggered += 1
                            break
                if 'spellowned' in triggers:
                    data = triggers['spellowned']
                    if isinstance(OWNED['SPELLS'][0],str):
                        for idx,repl in enumerate(OWNED['SPELLS']):
                            OWNED['SPELLS'][idx] = Magic.getSpell(self.getID(repl))
                    for i in range(len(data)):
                        if isinstance(data[i],str):
                            data[i] = self.getID(data[i])
                        if isinstance(data[i],int):
                            data[i] = Magic.getSpell(data[i])
                    if set(data).issubset(set(OWNED['SPELLS'])):
                        triggered += 1
                #
                #add in other trigger conditions
                #
                if triggered == len(triggers):
                    if SHOWDEBUG: print "Condition true"
                    if callable(procdamage):
                        procdamage = procdamage()
                    if AVGMODE == 'avg':
                        curproctotal += round((procdamage * procrate) / 100.0,2)
                    elif AVGMODE == 'max':
                        curproctotal += round(procdamage * 1.0,2)
                else:
                    if SHOWDEBUG: print "Condition false"
            if AVGMODE == 'max':
                if maxproc < curproctotal:
                    maxproc = curproctotal
                curproctotal = 0
            
            
        if AVGMODE == 'avg':
            return curproctotal
        elif AVGMODE == 'max':
            return maxproc
        else:
            return float('inf') if EXTRAFUNC == 'pessimal' else 0
    
#Overrides cls.spelllist with self.spelllist containing the magics that are
#only used during the compare for averaging purposes    
class MetaMagic(Magic):
    def __init__(self,*args):  #contains spell IDs, names, or Magic instances
        self.reset()
        mainspelllist = self.spelllist  #should reference main list
        newspelllist = []
        for arg in args:
            if isinstance(arg,int):
                newspelllist.append(self.getSpell(arg))
            elif isinstance(arg,str):
                newspelllist.append(self.getSpell(self.getID(arg)))
            else:
                newspelllist.append(arg)
        self.fullname = str([s.fullname for s in newspelllist])
        self.nickname = str([s.nickname for s in newspelllist])
        self.numspells = len(newspelllist)
        self.contains = newspelllist
        self.id = Magic.magic_id
        Magic.magic_id += 1
        Magic.spelllist.append(self)
        self.spelllist = newspelllist  #the hack
    def __repr__(self):
        return "[MetaMagic: ("+str(self.id)+") "+str(self.fullname)+"]"
        
    #   This method fills Magic.spelllist with all metamagic
    #   pairs that have a castable synergy to them.
    @classmethod
    def fillMetaPairs(cls):
        global DEBUGDOUBLES
        # Iterate through all spells
        for idx,spell in enumerate(Magic.spelllist):
            if len(spell.contains) > 1: continue #Do not process metaspells
            # Iterate over remaining spells to find a proc that uses spell
            for spellcmp in Magic.spelllist[idx:]:
                if spell in list(set(list(cls.getSpellcastProcs(spellcmp.id)))):
                    pair = [spell,spellcmp]
                    #Check our pair against magic list to see if it already exists
                    for spellchk in Magic.spelllist:
                        if set(spellchk.contains) == set(pair):
                            break
                    else:
                        #This runs if the loop passes through without collision
                        m = MetaMagic(pair[0].id,pair[1].id)
                        m.collateAverage(2)
                        if DEBUGDOUBLES: print "Spell pair: "+str(m.fullname)+" at average "+str(m.avgfound)
                        pass
                        
            
        
    #Generator that returns Magic objects that contain spells listed in
    #any of the input spell's 'spellcast' proc trigger(s)
    @classmethod
    def getSpellcastProcs(cls,spellID):
        spell = cls.getSpell(spellID)
        for procs in spell.proclist:
            for proc in procs[1]:
                triggers = proc[1]
                if 'spellcast' in triggers:
                    data = triggers['spellcast']
                    for i in range(len(data)):
                        if isinstance(data[i],str):
                            data[i] = cls.getID(data[i])
                        yield cls.getSpell(data[i])
    #
    
            
        
    

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
## This only heals the user and improve crit chance if Glimmering Moon is cast
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
m.newDmg(lambda : 3 * min(OWNED['TRP_INCINERATED_SOLDIER'],50))
m.newTrigTag('winter')
m.newDmg(lambda : 100 * OWNED['ARM_LIVING_FLAME'])
m.newTrigTag('winter')
m.newTrig('spellcast','Flame Serpent')
m.newDmg(150)
m.newProc(25)
#
m = Magic("Consume","cons")
m.newDmg(120)
m.newDmg( lambda : 40 * OWNED['GEN_BURUT_THE_HUNGRY'] )
m.newDmg( lambda :  5 * min(OWNED['ITM_TURKEY_OF_PLENTY'],5) )
m.newDmg( lambda :  5 * min(OWNED['ITM_DEER_OF_PLENTY'],5) )
m.newDmg( lambda :  5 * min(OWNED['ITM_BEAR_OF_PLENTY'],5) )
m.newDmg( lambda :  5 * min(OWNED['ITM_BOAR_OF_PLENTY'],5) )
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
#
m = Magic("Deep Freeze","deep")  #avoiding name collision with Dark Forest
m.newDmg(50)
m.newDmg( lambda : 10 * OWNED['GEN_HAIMISH'] ) 
m.newDmg( lambda : 10 * OWNED['GEN_OLD_DEAD_ELVIGAR'] ) 
m.newDmg( lambda : 10 * OWNED['GEN_UTHIN'] ) 
m.newDmg( lambda : 10 * OWNED['GEN_VILI'] ) 
m.newDmg( lambda : 15 * OWNED['ITM_CRYSTAL_OF_THE_DEADLY_COLD'] ) 
m.newDmg( lambda : 15 * OWNED['ITM_KINGSJAW'] ) 
m.newDmg( lambda : 15 * OWNED['ITM_DARKES_SIGHT'] ) 
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
#
m = Magic("Intoxicate","intox")
m.newDmg(75)
m.newDmg( lambda : 5 * OWNED['SET_JOVIAL_JESTER'] )
m.newDmg( lambda : 5 * OWNED['SET_CELEBRATION'] )
m.newTrigTag('festival')
m.newDmg(100)
m.newProc(15)
#
m = Magic("Invasive Growth","IG")
m.newTrigTag('beast')
m.newDmg(100)
m.newTrigTag('beast')
m.newDmg( lambda : 10 * OWNED['SET_FOREST_SENTINEL'] )
m.newProc(10)
#
m = Magic("Judgement","judge")
m.newDmg(200)
m.newDmg( lambda : 100 * OWNED['ARM_SABIRAHS_ASHES'] )
m.newDmg( lambda : 100 * OWNED['ARM_CERMARINAS_BLADE'] )
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
#
m = Magic("Levitate","lev")
m.newDmg(100)
m.newDmg( lambda : min(OWNED['ITM_STORMSHIP'],50) )
m.newDmg( lambda : min(OWNED['TRP_CLOUD_ELEMENTAL'],25) )
m.newTrigTag('qwiladrian')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Lightning Rod","LR")
m.newDmg(100)
m.newDmg( lambda : 25 * OWNED['GEN_PASITHEA'] )
m.newDmg( lambda : 25 * OWNED['GEN_BELLEFOREST'] )
m.newDmg( lambda : 25 * OWNED['GEN_ESCH'] )
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
m = Magic("Manifest Dread","MD")
m.newDmg(50)
m.newDmg( lambda : 3 * min(OWNED['TRP_SLEEPLESS_SOLDIERS'],50) )
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
#
m = Magic("Mark of the Griffin","MG")
m.newDmg(25)
m.newDmg( lambda : 2 * min(OWNED['TRP_GRIFFIN_CHAMPIONS'],100) )
m.newTrig('spellowned',"Mark of the Griffin")
m.newDmg(25)
m.newTrigTag('blackhand')
m.newDmg(300)
m.newTrigTag('war')
m.newDmg(300)
m.newProc(10)
#
m = Magic("Mark of the Infinite Dawn","MID")
m.newDmg(1980)
m.newTrigTag('dragon')
m.newDmg(lambda : 590 + 9 * OWNED['SET_INFINITE_DAWN'])
m.newTrigTag('worldraid')
m.newDmg(lambda : 590 + 9 * OWNED['SET_INFINITE_DAWN'])
m.newTrigTag('eventraid')
m.newDmg(lambda : 590 + 9 * OWNED['SET_INFINITE_DAWN'])
m.newTrigTag('elite')
m.newDmg(lambda : 590 + 9 * OWNED['SET_INFINITE_DAWN'])
m.newTrigTag('deadly')
m.newDmg(lambda : 590 + 9 * OWNED['SET_INFINITE_DAWN'])
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
#
m = Magic("Mystic Slaughterers","MS")
m.newDmg(10)
m.newDmg( lambda : 10 * OWNED['GEN_SIR_JORIM'] )
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
m = Magic("Obedience","OB")
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
#
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
m.newTrig('spellcast',"Mark of the Raven's Wing")
m.newTrig('spellowned',"Mark of the Raven's Wing")
m.newDmg(-25)
m.newTrig('spellcast',"Shadowstep")
m.newTrig('spellowned',"Shadowstep")
m.newDmg(-25)
m.newTrig('spellcast',"Inspire")
m.newTrig('spellowned',"Inspire")
m.newDmg(-25)
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
#
m = Magic("Quicksand Pit","QSP")
m.newDmg(60)
m.newDmg( lambda : 10 * OWNED['SET_BATTLE_SCARRED'] )
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
#
m = Magic("Rally","rally")
m.newTrigTag('guild')
m.newDmg(120)
m.newTrigTag('guild')
m.newTrig('spellcast',["Unity","Deathmark","Volatile Runes"])
m.newDmg(200)
m.newTrigTag('guild')
m.newDmg( lambda : 35 * OWNED['SET_SPIRIT_RAVEN'] )
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
#
m = Magic("Resurrect","res")
m.newDmg(75)
m.newDmg( lambda : OWNED['SET_RESURRECTION'] )
m.newTrig('spellowned',"Resurrect")
m.newDmg(75)
m.newTrigTag('undead')
m.newDmg(250)
m.newProc(10)
## Somewhat simplified. Additional 10% chance is represented as its own proc
m = Magic("Sandstorm","sand")
m.newDmg(15)
m.newProc(26)
m.newTrig('spellcast',"Blazing Sun")
m.newDmg(15)
m.newProc(10)
#
m = Magic("Sap Energies","sap")
m.newDmg(60)
m.newDmg( lambda : 10 * OWNED['SET_BATTLE_SCARRED'] )
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
## Abbreviation 'SM' changed to 'SaM' to avoid collision with Shattered Moon
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
#
m = Magic("Seven Unyielding","7U")
m.newDmg(95)
m.newDmg( lambda : 15 * OWNED['GEN_SAR_VELANIA_THE_RED'] )
m.newDmg( lambda : 15 * OWNED['GEN_SIR_BOHEMOND_THE_ORANGE'] )
m.newDmg( lambda : 15 * OWNED['GEN_SIR_EMERIC_THE_YELLOW'] )
m.newDmg( lambda : 15 * OWNED['GEN_SIR_AARON_THE_BLUE'] )
m.newDmg( lambda : 15 * OWNED['GEN_SIR_COLBAEUS_THE_GREEN'] )
m.newDmg( lambda : 15 * OWNED['GEN_SAR_MEURA_THE_INDIGO'] )
m.newDmg( lambda : 15 * OWNED['GEN_SAR_WENNI_THE_VIOLET'] )
m.newProc(8)
#Shadow Strike was omitted due to same reasons as Battousai
#
m = Magic("Shadowstep","SS")
m.newDmg(50)
m.newDmg( lambda : 15 * OWNED['SET_SHADOW-SLIP_ASSASSIN'] )
m.newTrigTag('demon')
m.newDmg(120)
m.newProc(10)
#
m = Magic("Shattered Moon","SM")
m.newDmg(200)
m.newDmg( lambda : 100 * OWNED['GEN_YING_OF_THE_SHATTERED_MOON'] )
m.newTrig('spellowned','Shattered Moon')
m.newDmg(100)
m.newTrigTag('human')
m.newDmg(750)
m.newProc(10)
#
m = Magic("Shrink","shrink")
m.newDmg(100)
m.newDmg( lambda : 10 * OWNED['SET_WEE_WARRIOR'] )
m.newTrig('spellowned',"Shrink")
m.newDmg(100)
m.newTrigTag('giant')
m.newDmg(350)
m.newProc(10)
# 
m = Magic("Siphon Strength","siphon")
m.newDmg(100)
m.newDmg( lambda : 5 * OWNED['SET_BRUTE_STRENGTH'] )
m.newTrig('spellowned',"Siphon Strength")
m.newDmg(45)
m.newTrigTag('goblin')
m.newDmg(200)
m.newTrigTag('orc')
m.newDmg(200)
m.newTrigTag('ogre')
m.newDmg(200)
m.newProc(10)
#
m = Magic("SMITE","SMITE")
m.setrare()
m.newDmg(500)
m.newDmg(lambda : 100 * OWNED['AUREATE_TROPHY'])
m.newDmg(lambda :  40 * OWNED['ARGENT_TROPHY'])
m.newDmg(lambda :  10 * OWNED['BRONZED_TROPHY'])
m.newTrig('spellowned',"SMITE")
m.newDmg(150)
m.newProc(22)
#
m = Magic("Soul Pilferer","SP")
m.newTrigTag('undead')
m.newDmg(300)
m.newTrigTag('undead')
m.newDmg( lambda : 5 * min(OWNED['TRP_GRAVE_GUARDIAN'],50))
m.newTrigTag('undead')
m.newTrig('spellcast',"Gravebane")
m.newDmg(400)
m.newProc(15)
# 
m = Magic("Stanzas of Slaughter","SoS")
m.newDmg(120)
m.newDmg( lambda : 5 * OWNED['SET_WARRIOR_POET'] )
m.newTrig('spellcast',"Harmony")
m.newDmg(50)
m.newTrig('spellcast',"Discord")
m.newDmg(50)
m.newProc(9)
#
m = Magic("Survivor","surv")
m.newDmg(60)
m.newDmg( lambda : 10 * OWNED['SET_BATTLE_SCARRED'] )
m.newTrigTag('orc')
m.newDmg(200)
m.newTrigTag('nightmarequeen')
m.newDmg(200)
m.newProc(10)
#
m = Magic("Sword of Light","SoL")
m.newDmg(100)
m.newDmg( lambda : 15 * OWNED['SET_RISING_DAWN'])
m.newTrigTag('dragon')
m.newDmg(150)
m.newProc(10)
## Somewhat simplified proc. Additional proc chance is represented as its own
m = Magic("Terracles' Blessing","TB")
m.newDmg(48)
m.newProc(12)
m.newTrig('spellcast',"Lyria's Swiftness")
m.newTrigTag('dragon')
m.newDmg(48)
m.newProc(3)
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
#
m = Magic("Violet Storm","VS")
m.newDmg(90)
m.newDmg( lambda : 5 * OWNED['SET_VIOLET_KNIGHT'] )
m.newProc(5)
#
m = Magic("Visions of the Deep","VotD")
m.newDmg(500)
m.newTrigTag(['terror','abyssal']) #OR condition. Apply proc once.
m.newDmg(lambda : 58 + 4 * OWNED['SET_DEPTH_TERROR'])
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
m.newDmg( lambda : 200 * OWNED['ITM_LEGEND_OF_THE_DEMIGOD'] )
m.newProc(20)
#
m = Magic("[LV 20,000]","#4#")
m.setrare()
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
    
if EXTRAFUNC in ['dumpnames','dumplist']:
    MetaMagic.fillMetaPairs()
    for spell in Magic.spelllist:
        print str(spell.fullname) + " / " + str(spell.nickname)
    sys.exit()
if EXTRAFUNC == 'dumpavg':
    MetaMagic.fillMetaPairs()
    for spell in Magic.spelllist:
        print str(spell.nickname) + ": " + str(spell.getAvg())
    sys.exit()
if EXTRAFUNC == 'count':
    spellcount = len(Magic.spelllist)
    print "Number of spells in database: "+str(spellcount)
    MetaMagic.fillMetaPairs()
    print "Number of metamagic in database: "+str(len(Magic.spelllist)-spellcount)
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
print "[Experimental] Raid Magic Optimizer"
print "Calc for tags: "+str(RAIDTAGS)
print MAIN_DIVIDER

MetaMagic.fillMetaPairs()
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










