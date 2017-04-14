#!/usr/bin/env python
# -*- coding: utf-8 -*-

# game_hierarchy.py

# defines structures for a live recording, with gaps for any analysis we want to run later
# class attribute lists have single item indentation to make it easier to change the display order
# I need to tweak the data storage for some actions/events/calls at runtime

# TODO: Validate inputs, check out https://github.com/alecthomas/voluptuous
# TODO: make the team order explicitly store offence and defence as categories instead of numbers

# store it once
# Imports
# Standard Library
import re


class Root(object):
    """Wrapper class for debugging."""

    def __init__(self, **kwargs):
        """Returns an AssertionError if any unexpected kwargs exist on initialisation."""

        print("Root.__init__() called.")

        assert not kwargs


"""
PEOPLE

classification levels for people in a game:
    - INDIVIDUAL: each player on each team
    - TEAM: each team considered as a whole
    - GAME: everyone in the game considered as a whole
    - TOURNAMENT: all players on all teams in all games considered as a whole
"""


# TODO: insert this class for a Worlds campaign.
class Group(Root):
    """Superclass for a group of teams; e.g. Bench Ultimate (Club) or Team Australia (International)."""

    group_types = [
        u"Club",
        u"International",
    ]

    def __init__(self, **kwargs):
        """Takes group_name, group_type as mandatory arguments."""

        print("Group.__init__({}) called.".format(kwargs))

        self.group_name = kwargs.pop("group_name")
        self.group_type = kwargs.pop("group_type")
        # self.group_teams = []  # list of pointers to Team Objects

        super(Group, self).__init__(**kwargs)


class Team(Root):  # change to inherit from Group when that's built
    """Data object for a team season; e.g. a Club Nationals or Worlds campaign."""

    def __init__(self, **kwargs):
        """Takes team, [team_players], team_division as mandatory arguments."""

        print("Team.__init() called.")

        self.team_name = kwargs.pop("team_name")
        self.team_players = kwargs.pop("team_players")
        self.division = kwargs.pop("division")

        # TODO: build a regex to extract gender and age from division
        # self.team_gender = kwargs.pop("team_gender")
        # self.team_age = kwargs.pop("team_age")

        age_strings = [
            'Junior/u20',
            'u24',
            'unrestricted',
            'masters',
            'grand masters',
            'great grand masters'
        ]
        gender_strings = [
            'open',
            'women',
            'mixed',
        ]

        self.games = []  # ANDY: this is just a place for me to play with team scrapes from worlds
        # self.team_tournaments = None  # TODO: work out database for storing games

        super(Team, self).__init__(**kwargs)

    def append_game(self, game):
        """Appends a game object to self.games"""

        # ANDY: this is for me to muck around with scraping

        print(self.games)
        print(game)

        self.games.append(game)

        print("Game appended to self.games.")

    def __str__(self):
        return self.team


class Player(Root):
    """"""

    def __init__(self, **kwargs):
        """Takes player, number, gender as mandatory arguments."""

        print("Player.__init__() called.")

        self.player = kwargs.pop("player_name") # sorry
        self.number = kwargs.pop("number")
        self.gender = kwargs.pop("gender")
        # I really like the length here.

        # TODO: analysis attributes go here

        super(Player, self).__init__(**kwargs)

    def __str__(self):
        return self.player


"""
GAME STRUCTURE

classification levels for games:
    - INDIVIDUAL: a single game
    - DIVISION: a game as part of all games in a division
    - TOURNAMENT: a game as part of all games at a tournament
"""


class Tournament(Root):
    """Superclass for Game, provides scoring and field information."""

    # class attributes
    surfaces = [
        u"grass",
        u"beach",
        u"indoor",
    ]
    # field_size = if grass, elif beach, elif indoor, else raise ValueError; conditional on surface
    levels = [
        u"club",
        u"international",
        u"league",
        u"hat",
        u"pickup",
    ]
    # formats = [u"round-robin", u"Swiss-elimination", "etc."]

    def __init__(self, **kwargs):
        """Takes tournament, year, point_cap, time_cap, timeouts, divisions as mandatory 
        arguments."""

        print("Tournament.__init__() called.")

        self.tournament = kwargs.pop("tournament")
        self.year = kwargs.pop("year")  # TODO: turn this into a regex
        # self.location = kwargs.pop("location")
        # self.surface = kwargs.pop("surface")
        self.point_cap = kwargs.pop("point_cap")
        self.time_cap = kwargs.pop("time_cap")
        self.timeouts = kwargs.pop("timeouts")
        self.divisions = kwargs.pop("divisions")
        # self.dates = None
        # self.format = None  # round-robin, single-elim, etc.

        super(Tournament, self).__init__(**kwargs)

    def __str__(self):
        return self.tournament

# TODO: define an abstract field class for heat maps; [x, y, z] with [0, 0, 0] as back left cone of defending end zone.


# TODO: work out database
class Division(Root):
    """Takes division_name and division_teams as mandatory arguments."""

    def __index__(self, **kwargs):
        """Takes division, division_teams as mandatory arguments."""

        print("Division.__init__() called.")

        self.division = kwargs.get("division")
        self.division_teams = kwargs.get("division_teams")

        super(Division, self).__init__(**kwargs)

    def __str__(self):
        return self.division


"""
SEQUENCE

classification levels for live game sequences:
    - INDIVIDUAL: a single item within a game
    - POSSESSION: all items from players on the same team for a possession
    - POINT: all items from all players for a point
    - GAME: all items from all players for all points in a game
"""


class TimeStamp(Root):
    """
    TimeStamps are datetime objects referring to the start and end of an Event.
    """

    def __init__(self, **kwargs):
        """Takes ts_start, ts_end as mandatory arguments."""

        self.ts_start = kwargs.pop("ts_start")
        self.ts_end = kwargs.pop("ts_end")
        self.ts_duration = self.ts_end - self.ts_start

        # if kwargs:  # ANDY - again Root will check this
        super(TimeStamp, self).__init__(**kwargs)


class Game(Tournament, TimeStamp):  # doesn't inherit from Division because it doesn't need division_teams
    """Data object for a game of Ultimate."""

    def __init__(self, **kwargs):
        """
        Takes a list of game_teams, game_stage, division as mandatory inputs. 
        """
        # TODO: work out how this input should happen

        print("Game.__init__() called.")

        self.game_score = [[0, 0]]  # double nesting, want to just append the score here after each point
        self.points = []
        self.game_teams = kwargs.pop("game_teams")
        self.game_stage = kwargs.pop("game_stage")

        self.division = kwargs.pop("division")

        # self.game_weather = kwargs.pop("game_weather")

        # TODO: build this to track how many nerds are ruined
        # self.flips = kwargs.pop("flips")

        super(Game, self).__init__(**kwargs)

    def __str__(self):
        self.game = "{}{}-{}:{}-{}".format(
            self.tournament,
            self.year,
            self.game_stage,
            self.game_teams[0].team,
            self.game_teams[1].team,
        )
        return self.game


class Point(TimeStamp):
    """"""

    # class attributes
    point_outcomes = [
        u"break",
        u"hold"
    ]
    # TODO: want to consider upwind/downwind at some point here too

    def __init__(self, **kwargs):
        """Takes point_teams, point_lines, point_score as a mandatory arguments."""

        print("Point.__init__() called.")

        self.point_teams = kwargs.pop("point_teams")  # [offence, defence]

        temp_lines = kwargs.pop("point_lines")  # [[offence_players], [defence_players]]
        self.point_lines = [temp_lines]  # nesting for subs
        self.line_set = 0  # pair of lines is a set - after sub, new set, increment
        # use current_lines()

        self.point_score = kwargs.pop("point_score")
        self.point_number = self.point_score[0] + self.point_score[1] + 1
        self.point_difference = [self.point_score[0] - self.point_score[1], None]
        # point_difference is a two item list of the relative offensive position at the start of the point:
        # positive numbers = winning, 0 = tied, negative numbers = losing

        self.sequences = []  # TODO: this changes with the new structure and might break things.
        self.turnovers = [[0, 0]]  # [offence, defence]
        self.possessions = [[1, 0]]  # [offence, defence]
        self.point_outcome = None  # from point_outcomes

        self.offence = 0  # starting offence is zero, this is to be able to track offence changes

        if kwargs:
            print(kwargs)
            super(Point, self).__init__(**kwargs)

    def current_lines(self):
        return self.point_lines[self.line_set]

    def update_lines(self,lines):
        # takes in [teamA_players, teamB_players]
        self.point_lines.append(lines)
        self.line_set+=1


class Sequence(TimeStamp):
    """Sequence is all actions in a point with the same group of players."""

    def __init__(self, **kwargs):
        """Takes sequence_lines as mandatory arguments."""

        print("Sequence.__init__() called.")

        # TODO: reorganise this so offence and defence are explicit
        self.sequence_lines = kwargs.pop("sequence_lines")
        self.possessions = []

        if kwargs:
            super(Sequence, self).__init__(**kwargs)


class Possession(Sequence, TimeStamp):
    """Superclass for Events from players on the same team."""

    def __init__(self, **kwargs):
        """Takes possession_team, as mandatory arguments."""

        print("Possession.__init__() called.")

        # making this optional for the sake of a running program @ div2 nats @ 31/3/17
        if 'possession_team' in kwargs:
            self.possession_team = kwargs.pop("possession_team")

        if kwargs:
            super(Possession, self).__init__(**kwargs)


class DiscStatus(Root):
    """
    Object for WFDF rule 8. Status of the Disc. 
    Used for the effect of calls and time outs on possession.
    """

    # class attribute - possible states for the disc
    status = [u"dead", u"live"]

    def __init__(self, **kwargs):
        """Takes disc_status, as mandatory inputs."""

        print("DiscStatus.__init__() called.")

        self.disc_start = kwargs.pop("disc_status")
        self.disc_end = kwargs.pop("disc_end")

        super(DiscStatus, self).__init__(**kwargs)


class Pull(Possession, DiscStatus):
    """"""

    # TODO: think about possession of the pull, I don't think it counts as the defensive team ever having possession.
    # might not need to inherit possession, if it's separate

    pull_buttons = [
        # out-of-bounds
        u"brick",
        u"sideline",  # TODO: build locations to store this
        # in
        u"caught",
        u"landed",
        u"touched",
        u"untouched",
        u"dropped-pull",
        # The Pottsy Rule
        u"offside",  # TODO: this is technically a call for storage purposes but might as well put it here
    ]

    # in_receptions = all_pulls[0:1]
    # ob_receptions = all_pulls[2:]

    def __init__(self, **kwargs):
        """Takes puller, pull_location, pull_reception as mandatory arguments."""

        print("Pull.__init__() called.")

        self.puller = kwargs.pop("puller")
        self.pull_action = kwargs.pop("pull_action")  # this is taken from all_pulls
        self.pull_location = None  # Set this off pull_action
        self.pull_reception = None  # as above
        # self.type = kwargs.pop("pull_type")

        super(Pull, self).__init__(**kwargs)


class DiscEvent(Possession, DiscStatus):
    """"""

    # class attributes
    # ANDY: these don't need to display, they're validation checks
    possessions = [
        u"offensive",
        u"defensive",
    ]
    types = [
        u"throw",
        u"reception",
    ]
    outcomes = [
        u"completion",
        u"turnover",
    ]

    # ANDY: these need to display
    all_actions = [
        # offensive
        # throws
        # completions
        u"pass",
        u"assist",
        # turnovers
        u"double-touch",
        u"down",
        u"hand-over",
        u"out-of-bounds",
        # receptions
        # completions
        u"catch",
        u"goal",
        # turnovers
        u"drop"
        # defensive
        # throws
        # completions
        u"marked-pass",
        u"tipped-pass",
        # turnovers
        u"foot-block",
        u"hand-block",
        u"stall-out",
        # receptions
        # completions
        u"marked-catch",
        # turnovers
        u"Callahan",
        u"block",
        u"intercept",
    ]

    # i should be doing all this shit by slicing the all_actions list maybe
    # way less readable tho

    turnover_actions = [
        u'double-touch',
        u'down',
        u'hand-over',
        u'out-of-bounds',
        u'drop',
        u'foot-block',
        u'hand-block',
        u'stall-out',
        u'block',
        u'intercept',
    ]

    # these categories are for visual display purposes
    primary_actions = [
        u'pass',
        u'down',
        u'drop',
        u'out-of-bounds',
        u'goal',
    ]

    secondary_actions = [
        u'stall-out',
        u'double-touch',
        u'hand-over',
    ]

    defensive_actions = [
        u'block',
        u'intercept',
        # u'Callahan',
    ]

    def __init__(self, **kwargs):
        """Takes event_player, event_action as mandatory arguments."""

        print("Event.__init__() called.")

        self.event_player = kwargs.pop("event_player")  # pointer to player object
        self.event_action = kwargs.pop("event_action")

        # TODO: set these off the action
        # setting these off the action is doable here
        # setting action things that require information from other points
        #   will have to be a function of the class where the other point is passed in at runtime
        self.action_possession = None
        self.action_type = None
        self.action_outcome = None
        # self.location = None

        # this feels weird am i doing this right
        if self.event_action in self.turnover_actions:
            print('event_action (in turnovers): '+self.event_action)
            self.action_outcome = self.outcomes[1]
        else:
            self.action_outcome = self.outcomes[0]

        if kwargs:
            super(DiscEvent, self).__init__(**kwargs)


class Call(TimeStamp, DiscStatus):
    """"""

    # class attributes
    call_buttons = [
        u"offside",
        u"time-out",
        u"pick",
        u"foul",
        u"strip",
        u"marking-infraction",
        u"travel",
        u"delay-of-game",
        u"equipment",
        u"delay-of-game",
        u"injury",
        u"down",
        u"out",
        u"time out"  # TODO: these need to trigger a different screen
    ]
    call_outcomes = [
        u"contested",
        u"offsetting-fouls"
        u"uncontested",
        u"retracted",
    ]

    def __init__(self, **kwargs):
        """Takes caller, call, call_against, call_outcome as mandatory arguments."""

        print("Call.__init__() called.")

        self.caller = kwargs.pop("caller")  # pointer to Player object
        self.call_made = kwargs.pop("call_made")
        self.call_against = kwargs.pop("call_against")  # pointer to Player object
        self.call_outcome = kwargs.pop("call_outcome")
        # TODO: game adviser/observer should probably go here

        super(Call, self).__init__(**kwargs)


class TimeOut(TimeStamp):
    """"""

    def __init__(self, **kwargs):
        """"""

        print("TimeOut.__init__() called.")

        self.to_team = kwargs.pop("to_team")
        self.to_caller = kwargs.pop("to_caller")
        self.to_category = kwargs.pop("to_category")  # live or dead disc

        super(TimeOut, self).__init__(**kwargs)
