# RATS_STATS

2017 motto ideas:
Construct Your Life

This is really out of date.


###################
Setting up the App:
###################

Prereqs:
- Latest copy of the .apk file

A folder called “stats” on your phone (at /sdcard/) with the following in it:
 - Folder called teamlists (with team list files in it)
 - U22.cfg

Your phone must be set to allow installation from unknown sources.

Run the .apk file.


##################
Using the App:
##################
##
##It’s not pretty, but it works. It’s a bit fragile, but it will take the stats and put them in a file.
##Don’t ask too many hard questions.
##

The menu has four options : take new stats, read old stats, switch config, and exit.
Read old stats will either crash the app or do nothing. Leave it alone.
Take new stats is where the actual stat-taking happens, but you have to select a config beforehand.


This is where switch configs comes in. Switch config will present you with the current config and ask if you need to switch,
        which you will every time you restart the app.
If you switch, you will be presented with two file lists, in /stats/teamlists.

Here select two teams to play each other - THIS DETERMINES THE FILENAME - and then confirm your selection.

Then go to take new stats, confirm the input is correct, and you’ll be at selecting who’s on offence.
 Then select puller, then the two lines of players, then you’re at select action.


This is the main screen and works as follows:
Select a player, then tap the action. The event won’t be stored until you tap the action so you can change the player until then.
 When you tap an action the player list should unselect all options. # don’t put actions without players pls #
There’s an ‘other’ button - combine with manual notes - and a gameover button that ends the game (and saves it) whenever you like.
 The block button does nothing yet.


The available players will switch each time you select an action that causes a turnover.
At the end of the point, you are asked if that was the game winner.
If so, the game ends and saves and you are returned to the menu.
If not, you now are returned to the select offence screen, to start a new point.


There’s no way to read the files (yet) but they’re just pickled Game objects.
