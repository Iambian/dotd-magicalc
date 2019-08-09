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

How to use
----------
If you haven't installed Python 2.7.x, install it now before going any further.

Open a command prompt in the directory/folder the script is and type

`python dotdmagi.py <N> [T1] ... [TN]`

* Where `N` is the number of magic slots the raid has
* Where `T1` through `TN` aret he tags (e.g. orc, dragon, deadly, etc.) that the raid has.

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

`python dotdmagi.py 8 deadly dragon shadowelf magicalcreature underground`

---
Example 3: You want to beat up poor Horgrak. Not even the deadly version, just
the poor, abused, oft-slaughtered kobold. He has two magic slots and no tags.

`python dotdmagi.py 2`

---
Example 4: Someone gave you a link to a Deadly Black Hand Lieutenant, and it's
your job to help magick it up. It has five magic slots and the tags `Black Hand , Winter , Human , Deadly`

`python dotdmagi.py 5 blackhand winter human deadly`

---

Modifying What The Script Assumes You Own
-----------------------------------------
Open up `dotdmagi.py' and scroll down to the line that starts with

`OWNED = {'

Below it are the entries full of stuff which the script uses to calculate procs
with based on what you own.

`'SPELLS'` is a list of all the magic you own. You can either use abbreviations
or full names.

Entries which contain either "True" (you own this item) or "False" (you do
not own this item) should only ever contain that.

Entries which contains numbers may only be non-negative whole numbers.

Known Issues (Script)
---------------------
* Magics that are heavily reliant on other cast magics, such as the Enigma type
  magic, may show up incorrectly in some cases due to list extension. This
  very problem is why I don't broadly share this utility, and it's not an easy
  one to solve. This can be partially mitigated by changing the `MAGICLIST_EXTEND`
  variable in the script to a lower number. In other cases, pairs that should
  show up but don't is because one or the other are unable to make the list
  on their own merits, and is thus considered not cast.
  
Known Issues (Magic)
---------------------
* Battousai, Brough's Trick, Buster 2.0, Haste, Leprechaun's Luck,
  Mad Marcia's Momentary Massacre, Magic Torch, Shadow Strike, Web of Aeons, and
  Wish were not added due to their procs not being quantifiable with
  available input, not available, or not usable.
* Beastmaster was simplified such that the script assumes your herd of mounts
  individually is at least 10,000 strong. That isn't hard to do these days.
* Abbreviations/nicknames were altered due to collisisons:
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
	  
License
-------
It's the MIT License. See `LICENSE` for more details.

Version History
---------------
* 0.1 - First release. Seems to largely work
* 0.2 - After some revisions and a lot of magic addons, the magic list is as
        complete as I want it to be. For now.
* 0.3 - Edited procs for additional correctness. Made tag input on command-line
        case-insensitive. Made the instructions more readable/skimmable.
		
		
		