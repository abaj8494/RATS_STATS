#!/usr/bin/env python
# -*- coding: utf-8 -*-

# game_hierarchy.py

# defines structures for a live recording, with gaps for any analysis we want to run later
# class attribute lists have single item indentation to make it easier to change the display order
# I need to tweak the data storage for some actions/events/calls at runtime

# TODO: Validate inputs, check out https://github.com/alecthomas/voluptuous
# TODO: make the team order explicitly store offence and defence as categories instead of numbers

# store it once


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
    - GAME: everyone in the game as a whole
    - TOURNAMENT: people across all games of a tournament
"""


# TODO: insert this class for a Worlds campaign.
class Group(Root):
    """Superclass for a group of teams; e.g. Bench Ultimate (Club) or Team Australia (International)."""

    group_types = [
        u"Club",
        u"International",
    ]

    def __init__(self, **kwargs):
        """Takes group_name as mandatory arguments."""

        print("Group.__init__({}) called.".format(kwargs))

        # self.group_name = kwargs.pop("group_name")
        # self.group_teams = []  # list of pointers to Team Objects
        # self.group_type = kwargs.pop("group_type")

        if kwargs:
            super(Group, self).__init__(**kwargs)


class Team(Root):
    """Data object for a team season; e.g. a Club Nationals or Worlds campaign."""

    def __init__(self, **kwargs):
        """Takes team_name, [team_players], team_division as mandatory arguments."""

        print("Team.__init() called.")

        self.team_name = kwargs.pop("team_name")
        self.team_players = kwargs.pop("team_players")
        # self.team_gender = kwargs.pop("team_gender")
        # self.team_age = kwargs.pop("team_age")

        # games have a division property - this is on hold
        # TODO: ANDY - doesn't need to be on hold, just needs to check that the team division matches the game division
        if 'team_division' in kwargs:
            self.team_division = kwargs.pop("team_division")

        self.games = []  # ANDY: this is just a place for me to play with team scrapes from worlds
        # self.team_tournaments = None  # TODO: work out database for storing games

        if kwargs:
            super(Team, self).__init__(**kwargs)

    def append_game(self, game):
        """Appends a game object to self.games"""

        # ANDY: this is for me to muck around with scraping

        print(self.games)

        self.games.append(game)

        print("Game appended to self.games.")

    def __str__(self):
        return self.team_name


class Player(Team):
    """"""

    def __init__(self, **kwargs):
        """Takes player_name, player_number as mandatory arguments."""

        print("Player.__init__() called.")

        self.player_name = kwargs.pop("player_name")
        self.player_number = kwargs.pop("player_number")

        # TODO: analysis attributes go here
        if kwargs:
            super(Player, self).__init__(**kwargs)

    def __str__(self):
        return self.player_name


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
        """Takes tournament_name, tournament_year, point_cap, time_cap, time_outs, tournament_division as mandatory 
        arguments."""

        print("Tournament.__init__() called.")

        self.tournament_name = kwargs.pop("tournament_name")
        self.tournament_year = kwargs.pop("tournament_year")  # TODO: turn this into a regex
        # self.tournament_location = kwargs.pop("tournament_location")
        # self.tournament_surface = kwargs.pop("tournament_surface")
        self.point_cap = kwargs.pop("point_cap")
        self.time_cap = kwargs.pop("time_cap")
        self.timeouts = kwargs.pop("timeouts")
        # self.tournament_divisions = kwargs.pop("tournament_divisions")
        # self.tournament_start = None
        # self.tournament_finish = None
        # self.tournament_duration = self.tournament_finish - self.tournament_start
        # self.tournament_format = None  # round-robin, single-elim, etc.

        # if kwargs:  # ANDY - there shouldn't be any, but Root will check this so I don't want the if here
        super(Tournament, self).__init__(**kwargs)

    def __str__(self):
        return self.tournament_name

# TODO: define an abstract field class for heat maps; [x, y, z] with [0, 0, 0] as back left cone of defending end zone.


# TODO: work out database
class Division(Tournament):
    """Takes division_name and division_teams as mandatory arguments."""

    def __index__(self, **kwargs):
        """Takes division_name, division_teams as mandatory arguments."""

        print("Division.__init__() called.")

        self.division_name = kwargs.get("division_name")
        self.division_teams = kwargs.get("division_teams")

        if kwargs:
            super(Division, self).__init__(**kwargs)


"""
SEQUENCE

classification levels for live game sequences:
    - INDIVIDUAL: a single item within a game
    - POSSESSION: all items from players on the same team for a possession
    - POINT: all items from all players for a point
    - GAME: all items from all players for all points in a game
"""


class Game(Division):
    """"""

    def __init__(self, **kwargs):
        """Takes a two-item list of game_teams (0=offence, 1=defence), game_stage as mandatory inputs. """
        # TODO: work out how this input should happen

        print("Game.__init__() called.")

        self.game_score = [[0, 0]]  # double nesting, want to just append the score here after each point
        self.points = []
        self.game_teams = kwargs.pop("game_teams")
        self.game_stage = kwargs.pop("game_stage")
        self.game_name = "{}{}-{}:{}-{}".format(
            self.tournament_name,
            self.tournament_year,
            self.game_stage,
            self.game_teams[0].team_name,
            self.game_teams[1].team_name
        )
        # self.game_start = None
        # self.game_finish = None
        # self.game_pause = None
        # self.game_weather = kwargs.pop("game_weather")

        if kwargs:
            super(Game, self).__init__(**kwargs)

    def __str__(self):
        return self.game_name


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

        self.sequence = []
        self.turnovers = [[0, 0]]  # [offence, defence]
        self.possessions = [[1, 0]]  # [offence, defence]
        self.point_outcome = None  # from point_outcomes

        self.offence = 0  # starting offence is zero, this is to be able to track offence changes

        if kwargs:
            print(kwargs)
            super(Point, self).__init__(**kwargs)

    def current_lines(self):
        return self.point_lines[self.line_set]


class Possession(TimeStamp):
    """Superclass for Events from players on the same team."""

    def __init__(self, **kwargs):
        """Takes possession_team, as mandatory arguments."""

        print("Possession.__init__() called.")

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

    all_pulls = [
        # out-of-bounds
        u"brick",
        u"sideline",
        # in
        u"caught",
        u"landed",
        u"touched",
        u"untouched",
        u"dropped-pull",
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

        if kwargs:
            super(Pull, self).__init__(**kwargs)


class Event(Possession, DiscStatus):
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
            super(Event, self).__init__(**kwargs)


class Call(TimeStamp, DiscStatus):
    """"""

    # class attributes
    calls = [
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

        if kwargs:
            super(Call, self).__init__(**kwargs)


class TimeOut(TimeStamp):
    """"""

    def __init__(self, **kwargs):
        """"""

        print("TimeOut.__init__() called.")

        self.to_team = kwargs.pop("to_team")
        self.to_caller = kwargs.pop("to_caller")
        self.to_category = kwargs.pop("to_category")  # live or dead disc

        if kwargs:
            super(TimeOut, self).__init__(**kwargs)
