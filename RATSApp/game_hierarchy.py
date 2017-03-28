#!/usr/bin/env python
# -*- coding: utf-8 -*-

# game_hierarchy.py

# defines structures for a live recording, with gaps for any analysis we want to run later
# class attribute lists have single item indentation to make it easier to change the display order
# App button options should call class attributes (rather than the floating lists we had before)
# I need to tweak the data storage for some actions/events/calls at runtime

# TODO: I can't work out what needs to inherit from what - currently everything inherits everything up the structure


class Root(object):
    """Wrapper class for debugging."""

    def __init__(self, **kwargs):
        """Throws an error if any unexpected kwargs exist on creation."""

        print("Root.__init__() called.")

        assert not kwargs


# TODO: insert this class
class Group(Root):
    """Superclass for a group of teams; e.g. Bench Ultimate (Club) or Team Australia (International)."""

    group_types = [
        u"Club",
        u"International",
    ]

    def __init__(self, **kwargs):
        """Takes group_name as mandatory arguments."""
        # TODO: it doesn't actually, turned this off until we're on a Worlds campaign.

        print("Group.__init__({}) called.".format(kwargs))

        # self.group_name = kwargs.pop("group_name")
        # self.group_teams = []  # list of pointers to Team Objects
        # self.group_type = kwargs.pop("group_type")

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
        self.team_division = kwargs.pop("team_division")

        self.games = []  # ANDY: this is just a place for me to play with team scrapes from worlds
        # self.team_tournaments = None  # TODO: work out database for storing games

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

        super(Player, self).__init__(**kwargs)


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
    ]
    # formats = [u"round-robin", u"Swiss-elimination", "etc."]

    def __init__(self, **kwargs):
        """Takes tournament_name, tournament_year, point_cap, time_cap, time_outs, tournament_division as mandatory 
        arguments."""

        print("Tournament.__init__() called.")

        self.tournament_name = kwargs.pop("tournament_name")
        # self.tournament_year = kwargs.pop("tournament_year")  # TODO: turn this into a regex
        # self.tournament_location = kwargs.pop("tournament_location")
        # self.tournament_surface = kwargs.pop("tournament_surface")
        self.point_cap = kwargs.pop("point_cap")
        self.time_cap = kwargs.pop("time_cap")
        self.time_outs = kwargs.pop("time_outs")
        self.tournament_divisions = kwargs.pop("tournament_divisions")
        # self.tournament_start = None
        # self.tournament_finish = None
        # self.tournament_duration = self.tournament_finish - self.tournament_start

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

        super(Division, self).__init__(**kwargs)


class Game(Division):
    """"""

    def __init__(self, **kwargs):
        """Takes a two-item list of game_teams (0=offence, 1=defence), game_stage as mandatory inputs. """

        print("Game.__init__() called.")

        self.game_score = [[0, 0]]  # double nesting, want to just append the score here after each point
        self.game_points = []
        self.game_teams = kwargs.pop("game_teams")
        self.game_stage = kwargs.pop("game_stage")
        self.game_name = "{}-{}:{}-{}".format(
            self.tournament_name,
            self.game_stage,
            self.game_teams[0].team,
            self.game_teams[1].team
        )
        # self.game_start = None
        # self.game_finish = None
        # self.game_pause = None
        # self.game_weather = kwargs.pop("game_weather")

        super(Game, self).__init__(**kwargs)

    def __str__(self):
        return self.game_name


class Point(Game):
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

        temp_lines = kwargs.pop("point_lines") # [[offence_players], [defence_players]]
        self.point_lines = [[temp_lines[0]], [temp_lines[1]]]  # nesting for subs

        self.point_score = [kwargs.get("point_score"), None]
        self.point_number = self.point_score[0][0] + self.point_score[0][1] + 1
        self.point_difference = [self.point_score[0][0] - self.point_score[0][1], None]
        # point_difference is a two item list of the relative offensive position at the start of the point:
        # positive numbers = winning, 0 = tied, negative numbers = losing

        self.sequence = []  # double nesting is to allow for injuries
        self.turnovers = [[0, 0]]  # [offence, defence]
        self.possessions = [[1, 0]]  # [offence, defence]
        self.point_outcome = None  # from point_outcomes

        self.time_stamp = None  # TODO: this only needs to be inherited by TimeOut, Pull, Event, Call

        super(Point, self).__init__(**kwargs)


class Pull(Point):
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

        super(Pull, self).__init__(**kwargs)


class Event(Point):
    """"""

    # class attributes
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

    def __init__(self, **kwargs):
        """Takes event_player, event_action as mandatory arguments."""

        print("Event.__init__() called.")

        self.event_player = kwargs.pop("event_player")  # pointer to player object
        self.event_action = kwargs.pop("event_action")

        # not sure about below names but type is restricted
        # TODO: set these off the action
        self.action_possession = None
        self.action_type = None
        self.action_outcome = None
        # self.location = None

        super(Event, self).__init__(**kwargs)


class Call(Point):
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
        self.call = kwargs.pop("call")
        self.call_against = kwargs.pop("call_against")  # pointer to Player object
        self.call_outcome = kwargs.pop("call_outcome")
        # TODO: game adviser/observer should probably go here

        super(Call, self).__init__(**kwargs)


class TimeOut(Point):
    """"""

    def __init__(self, **kwargs):
        """"""

        print("TimeOut.__init__() called.")

        self.to_team = kwargs.pop("to_team")
        self.to_caller = kwargs.pop("to_caller")
        self.to_category = kwargs.pop("to_category")  # live or dead disc

        super(TimeOut, self).__init__(**kwargs)
