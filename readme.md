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

This utility is designed to find the best (and next-to-best) magic for any raid
given its tags, which are supplied on the command-line, and the user's status
and parameters (e.g. number of mounts owned) in the script itself.

How to use
----------
Assuming you've installed Python 2.7.x (3.x will probably fail horribly), open
up a command prompt wherever the script is and type `python dotdmagi.py <N> [T1] ... [TN]`
where `N` is the number of magic slots the raid has, and `T1` through `TN` are
the tags (e.g. orc, dragon, deadly, etc.) that the raid has.

Example 1: You want to find the optimal magic setup for the raid Deadly Drakontos.
You look up the raid and find that it has eight magic slots and
the tags `Deadly , Aquatic , Dragon , Terror`. You would type the following into
the command-line:

`python dotdmagi.py 8 deadly aquatic dragon terror`

Example 2: You want to do the same with Deadly Vas'ok. It too has eight magic
slots, but has a load more tags: `Deadly , Dragon , Shadow Elf , Magical Creature , Underground`

`python dotdmagi.py 8 deadly dragon shadowelf magicalcreature underground`

Example 3: You want to beat up poor Horgrak. Not even the deadly version, just
the poor, abused, oft-slaughtered kobold. He has two magic slots and no tags.

`python dotdmagi.py 2`

Example 4: Someone gave you a link to a Deadly Black Hand Lieutenant, and it's
your job to help magick it up. It has five magic slots and the tags `Black Hand , Winter , Human , Deadly`

`python dotdmagi.py 5 blackhand winter human deadly`

Modifying What The Script Assumes You Own
-----------------------------------------
If you open up `dotdmagi.py` in a text/code editor (**NOT** a word processor. Those
will mangle the source), look a few lines down for the line that starts with
`OWNED`. That signals the start of the dictionary showing what the script assumes
you own. Most significant are the mounts you own, number of legions, and what
spells you own.

Most entries are straightforward; they require no explanation. `SPELLS`, on the
other hand, is a list which can contain either spell abbreviation/nicknames or
their full name. You should probably use the full name, as they are exactly as
they appear in-game, including capitalization and punctuation.


Known Issues (Script)
---------------------

* Some abbreviations listed aren't actually used by the community at large. This
  is either because I don't know them, or there's another spell with the same
  abbreviation. For technical reasons, abbreviation collision results in
  unpredictable behavior if you try to use them in the script, and I don't want
  that. At all.
* All tags had their spaces stripped to form a single word for each. This is a 
  limitation of the command-line interface without needing to use a bunch of quotes
* All tags are also lowercase. Searches are case-sensitive and if you include any
  capital letters in the names, they're skipped.
* If you edit ANYTHING inside the script, all names are case-sensitive too.
  Including spell names and abbreviations/nicknames.
* There are quite a few magics whose calculations have been simplified, either
  via manual calculation or by removing their effect altogether (as it's not
  expected many, if any, will meet those requirements). Those simplifications
  are noted with the magic definition.
* Magics that are heavily reliant on other cast magics, such as the Enigma type
  magic, may show up incorrectly in some cases due to list extension. This
  very problem is why I don't broadly share this utility, and it's not an easy
  one to solve. This can be partially mitigated by changing the `MAGICLIST_EXTEND`
  variable in the script to a lower number
  
Known Issues (Magic)
---------------------
* Battousai, Brough's Trick, Leprechaun's Luck, Mad Marcia's Momentary Massacre, 
  Shadow Strike, and Web of Aeons were omitted (not entered as comparable entries)
  due to requiring additional imput (such as raid time remaining) which would've
  made things both awkward and cumbersome.
* Haste was also omitted because it touches things I didn't want to touch, not 
  even with a ten foot pole
* Buster 2.0, Magic Torch, and Wish were also omitted. For different reasons, but
  they all boil down to either being unavailable or unusable (for the purpose of
  damage debuffing a raid)
* Blessing of Mathala, Blood Moon, Boil, Bramblewire Trap, Conflagration, Corrode,
  Desiccate, Djinnpocalypse, Dune Tears, Fearless Advance, Fey Flame, Free Will,
  From Iirhine With Love, Hailstorm, Inspire, Intoxicate, Invasive Growth, Judgement,
  Levitate, Lightning Rod, Mark of the Griffin, Mark of the Infinite Dawn, Shadowstep,
  Mystic Slaughterers, Quicksand Pit, Rally, Resurrect, Sap Energies,
  Shattered Moon, Shrink, Siphon Strength, SMITE, Soul Pilferer, Stanzas of Slaughter,
  Survivor, Visions of the Deep, and [That magic you get at lv 10,000 whose name depends
  on the platform you play] ... all want to check on pieces of equipment that I
  refuse to add to the `OWNED` dictionary, lest it get cluttered by things and confuse
  anyone wanting to edit it. Also, these are things that a typical player won't be
  expected to own and in many cases, don't make too much of a difference in the face
  of all the recent overpowred magics. These procs were nixed.
* Beastmaster, Consume, Deep Freeze, Doorway, Enraged Feeding Frenzy, Eternal Sight,
  Exorcism, Fatal Aim, Feeding Frenzy, Guster's Fault, Hemorrhage, Insanity Laughs,
  Manifest Dread, Seven Unyielding, Sword of Light, and Violet Storm had procs that
  were simplified by assuming certain things. Most of these assumes that if you
  own the magic, then you also likely own all the other parts that makes the magic
  more powerful. These procs were precalculated and added on as per their normal
  trigger conditions.
* Sandstorm and Terracles' Blessing have procs that modify the proc rate instead
  of simply adding more damage. The current system can't do that without a bit
  of rethinking things, so I did some math to simulate what extra damage it would
  do and then apply that instead.
* Purify has a problem because I can't do an OR-type operation with procs that
  share a single proc damage value with the current setup. I just made it so
  each condition adds their own proc value to the bunch. Haven't figured out a
  real workaround yet.

License
-------
It's the MIT License. See `LICENSE` for more details.

Version History
---------------
* 0.1 - First release. Seems to largely work
* 0.2 - After some revisions and a lot of magic addons, the magic list is as
        complete as I want it to be. For now.
