DotD Magic Calculator
=====================

Requirement(s)
--------------
* Python 2.7.x

What is this?
-------------
Magic. It's a great thing. Stick it on raids and watch the damage go up. But
people get real picky about which to apply where, and others have problems
keeping up with what the best should be.

This utility is designed to help find the best (and next-to-best) magic for any
raid given its tags, which are supplied on the command-line, and the user's
status and parameters (e.g. number of mounts owned) in the script itself.

The default configuration for the script is for (mostly) f2p players who have
been playing for a long (4+ years) time and have focused on obtaining premium
troops/generals, while sometimes splurging a bit on NIPs and other special
limited time events.

How to use
----------
If you haven't installed Python 2.7.x, install it now before going any further.
NOTE: If you have to install Python as a Windows user, ensure that Python is
added to your PATH variable during installation; this isn't checked on by default.

Open a command prompt in the directory/folder the script is and type

`python dotdmagi.py <N> [T1] ... [TN]`

* Where `N` is the number of magic slots the raid has
* Where `T1` through `TN` aret he tags (e.g. orc, dragon, deadly, etc.) that the raid has.
* `T1` through `TN` may also contain additional options which affects the script
	* `profile=maxed` sets the OWNED dictionary to max out everything. All the troops. All the items. All the everything.
	* `profile=alt` sets the OWNED dictionary to have the sort of things that a general purpose raid summoning alt account may have. Also what a new(-ish) player could have.
	* `raremagic=true` allows for the use of rare magics
	* `avgmode=max` changes optimization to highest proc damage, for leaderboard hits.

Examples
--------

---
Example 1: You want to find the optimal magic setup for the raid Deadly Drakontos.
You look up the raid and find that it has eight magic slots and
the tags `Deadly , Aquatic , Dragon , Terror`. You would type the following into
the command-line:

`python dotdmagi.py 8 deadly aquatic dragon terror`

---
Example 2: You want to do the same with Deadly Vas'ok. It too has eight magic
slots, but has a load more tags: `Deadly , Dragon , Shadow Elf , Magical Creature , Underground`
The people who want to magic this raid also has the good stuff. Rare stuff.

`python dotdmagi.py 8 raremagic=true deadly dragon shadowelf magicalcreature underground`

---
Example 3: You want to beat up poor Horgrak. Not even the deadly version, just
the poor, abused, oft-slaughtered kobold. He has two magic slots and no tags.

`python dotdmagi.py 2`

---
Example 4: Someone gave you a link to a Deadly Black Hand Lieutenant, and it's
your job to help magick it up. It has five magic slots and the tags
`Black Hand , Winter , Human , Deadly`. This privately shared raid is also going
to be hit by a bunch of high-rolling people, so they'll want it magick'd up accordingly.

`python dotdmagi.py 5 profile=maxed blackhand winter human deadly`

---
Example 5: You have a bunch of alt accounts. They're poor and destitute, but you're
trying to turn their lives around. So you summon up a Zugen in the hopes that they
can nab that [Weaponsmith Scroll 5](https://dotd.fandom.com/wiki/Weaponsmith_Scroll_5).
Thing is, you gotta pick magics that are friendly for the needy. This raid has
just one tag: `Ogre`. It has four magic slots. Pick wisely!

`python dotdmagi.py 4 profile=alt ogre`

Or just let the script pick for you.

---
Example 6: Someone gave you a link to a private Deadly Erebus and they want you
to help out with magic. Thing is, they want to keep it under wraps so they can
work it for leaderboard (Destroyers) hits. This raid has 10 magic slots and the
tags `Deadly, Dragon`, and you can safely assume that the guys hitting this raid
are totally tricked out.

`python dotdmagi.py 10 avgmode=max profile=maxed deadly dragon`

---

Modifying What The Script Assumes You Own
-----------------------------------------
Open up `dotdmagi.py` and scroll down to the line that starts with

`OWNED = {`

Below it are the entries full of stuff which the script uses to calculate procs
with based on what you own.

`'SPELLS'` is a list of all the magic you own. You can either use abbreviations
or full names.

Entries which contain either `True` (you own this item) or `False` (you do
not own this item) should only have one of those two options.

Entries which contains numbers may only be non-negative whole numbers.

Known Issues (Script)
---------------------
* Magics that depend on other magics being cast may not return correctly. Work
  has been done to solve this, but no rigorous testing has been done. Be aware
  of this possibility.
  
Known Issues (Magic)
---------------------
* Battousai, Brough's Trick, Buster 2.0, Haste, Leprechaun's Luck,
  Mad Marcia's Momentary Massacre, Magic Torch, Shadow Strike, Web of Aeons, and
  Wish were not added due to their procs not being quantifiable with
  available input, not available, or not usable.
* Beastmaster was simplified such that the script assumes your herd of mounts
  individually is at least 10,000 strong. That isn't hard to do these days.
* Abbreviations/nicknames were altered due to collisions:
	* "Guilbert's Banquet" renamed "GuB" due to Gravebane (GB) existing.
	* "Heaven's Kiss" was renamed (by PureEnergy, thanks a lot) "HvK" (despite
	  "HKi" making more sense). This avoids collision with Hell's Knell (HK).
    * "Intoxicate" named "intox" because Intermission (int) is more important.
	* "Savage Melodies" named "SaM" because Shattered Moon (SM) is still in
	  popular use. Despite this, both are still abbreviated "SM" due to use-case
	  context. (SaM only used on giants and SM only used on humans, and there is
	  as of yet no raid that has both tags)
    * "Shadowstep" was given "SS" although "Shadow Strike" made more sense. It is
	  this way only because the latter magic was omitted (see further above).
	* There are three magics that could have been abbreviated as "dis", which are
	  "Disintegrate", "Dismantle", and "Discord". Those were abbreviated as
	  "disi", "dism", and "disc", respectively.
* The magics you get at levels 2500, 5000, 10000, and 20000 are not given names
  since they depend on the platform you play on. They are instead listed as the
  level in which you get those magics. It is up to you to interpret them under
  the correct name.
	  
License
-------
It's the MIT License. See `LICENSE` for more details.

Additional Modes of Operation
-----------------------------
Instead of displaying optimal magics, the script can do other things. Most of
these exist for debugging purposes, but they might be useful to you.

* `python dotdmagi.py dumpnames` displays all registered name/abbreviation pairs,
  including doubles for sorting purposes
* `python dotdmagi.py selftest` performs various internal consistency checks
  and displays the results of those checks.
* `python dotdmagi.py dumpavg` displays all spells and pairs with their averages
  calculated. Assumes no tags nor any synergies were applied.
* `python dotdmagi.py count` displays the number of spells and automatically
  generated spell pairs (metamagic).
* `python dotdmagi.py find=[spellname]` searches the database for the spellname
  or abbreviation (w/o brackets) and prints the found spell's name and abbreviation
  pair. If the name contains spaces, you must enclose the whole name in quotes.
  These searches are case-insensitive.
  * Example 1: `python dotdmagi.py find=ToTH`
  * Example 2: `python dotdmagi.py find="Traditions of the Hunt"`
* `python dotdmagi.py proc=[spellname]` searches the database for the spellname
  or abbreviation (w/o brackets) and prints the proc information it finds.
  If the name contains spaces, you must enclose the whole name in quotes.
  These searches are case-insensitive.
  * Example 1: `python dotdmagi.py proc=MID`
  * Example 2: `python dotdmagi.py proc="Mark of the Infinite Dawn"`
  
Support for Python 3
--------------------

Another copy of the script was generated via the [2to3 tool](https://docs.python.org/2/library/2to3.html)
to hopefully run with Python3. Cursory testing shows that it does not immediately
crash and burn, so run it with care.

To use this, instead of doing

`python dotdmagi.py`

do this instead:

`py dotdmagi3.py`

All parameters used will be the same as with the original script

Example: `py dotdmagi3.py 10 deadly dragon`


Version History
---------------
* 0.1 - First release. Seems to largely work
* 0.2 - After some revisions and a lot of magic addons, the magic list is as
        complete as I want it to be. For now.
* 0.3 - Edited procs for additional correctness. Made tag input on command-line
        case-insensitive. Made the instructions more readable/skimmable.
* 0.4 - Easter egg(s) w(as|ere) added. Performance was improved on very long `OWNED['SPELLS']`
		lists. Work was done to try to solve the problem of calculating cast magic
		synergies. Profiles added. A toggle to allow use of rare magics added. Added
		a switch to allow optimization for leaderboard hits.
* 0.5 - Made internal magic name and abbreviation searches case-insensitive.
		Made the database user-searchable via find and proc commands
* 0.51- Added another magic
		
		