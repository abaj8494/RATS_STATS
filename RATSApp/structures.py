#!/usr/bin/env python
# -*- coding: utf-8 -*-

# structures.py (formerly definitions)

# we'll use this to be able to globally reference constants
# at the top of the file just put 'definitions'
# and then use definitions.variable

###
#  NOTE:
#   pull outcomes and actions MUST have unique names
#  # not sure if this is still true with kivy, best not to push our luck


cfg_filename = 'smo.cfg'
# we can do this whole thing better post-smo
# the plan is to be able to select it from inside the program, and then it'll be saved as a property of the game
# for later extraction etc

# actions doesn't include blocks/interceptions because it needs to pull a player from the other team list. This should
# probably display in order of use once we have some numbers (ie who has ever called handover?).
actions = [
    u'pass',
    u'drop',
    u'down',
    u'out-of-bounds',
    u'stall-out',
    u'deflection',
    u'double touch',
    u'hand-over',
    # u'uncontested offensive foul',
    u'violation',
    u'goal',
]

turnovers = [
    u'deflection',
    u'double touch',
    u'down',
    u'hand-over',
    u'out-of-bounds',
    u'stall-out',
    u'uncontested offensive foul'
]  # doesn't have goals or blocks, done separately BUT NOT FOR LONG


# Andy 17-03-06: renamed pull outcomes to have an underscore, added brick outcomes
# TODO: pop-up with brick outcomes
pull_outcomes = [u'caught', u'landed', u'dropped pull', u'touched', u'untouched', u'brick']
pull_outcomes_turnovers = [u'dropped pull']
brick_outcomes = [u'sideline', u'brick mark']


# TODO: rename these so that they actually make sense
class Game(object):
    def __init__(self, tournament, time_cap, points_cap, both_teams, both_names):
        self.tournament = tournament
        self.time_cap = time_cap
        self.points_cap = points_cap
        self.team_players = both_teams  # two item list
        self.team_names = both_names  # two item list
        self.time_game_start = None
        self.time_game_end = None
        self.paused_time = None
        self.score = [0, 0]
        self.points_list = []

    def __repr__(self):
        return u"Game Object" + unicode(self.team_names)

    __str__ = __repr__


class Point(object):
    def __init__(self, lines=[], offence=-1):
        # we don't know the time when we instantiate the Point, that comes at the pull

        self.lines = lines  # lines is a two item list, with 0 as current offence
        self.sequence = []
        self.time_start = None
        self.time_end = None
        self.starting_offence = offence
        self.scoring_team = 0  # unassigned initially
        self.pull = [u'unassigned puller', u'default outcome']

    def __repr__(self):
        return u"Point Object" + unicode(self.sequence)

    __str__ = __repr__