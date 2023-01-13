# Bejeweled 3 World Championships
A Python application that latches onto Bejeweled 3's memory addresses* to create a Nintendo World Championships type challenge.

*This is the reason I call the program a 'parasite', as it isn't a mod of the game.

This repository contains the actual parasite and a tkinter GUI to create challenges.
Users will have to install the [ReadWriteMemory](https://pypi.org/project/ReadWriteMemory/) module and the [psutil](https://pypi.org/project/psutil/)
module.

For documentation regarding the actual program, see [the Google Doc](https://docs.google.com/document/d/1RMc6QYoLbh4WKirbTtwDfBR7-BULapBkJrw-ORYdfP8/edit?usp=sharing).

# Known bugs

+ Sometimes does not detect restarts/game overs. Highest priority bug at the moment, as it can completely stall, and ruin, a run.
+ Quest related sub-challenges can be automatically skipped.

# Things that haven't been implemented yet

+ Timed sub-challenges that involve 'getting the highest X' (e.g. Column Combo in Ice Storm, Cascade, amount of gems cleared in one move). This one is half-completed, but I need to figure out how to properly implement these sub-challenges. Making the score the highest number in the condition would lead to some very boring scores (the ones listed above usually don't go above 20)
+ Numerous planned sub-challenges (Diamond Mine: Depth, Treasure Count, Match/Time Bomb: Endless Mode, Quest Mode: Completed Quests)
