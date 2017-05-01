# raw_game_hierarchy.py
# made from game_hierarchy.py @ 28/4/17 - thank you andy

# separation of concerns - this is minimally complex
# it will hold all the data taken from the game in the simplest structure
# such that it can be read into game_analysis.py to give useful numbers

# Timestamp and Root are never going to be instantiated on their own, only for superclassing
# Team, Player, Point, Event objects will be instantiated multiple times
# Game will only be created once per game taken


class Root(object):
    # Wrapper class for debugging.

    def __init__(self, **kwargs):
        # Returns an AssertionError if any extraneous variables exist upon an __init__() call.
        print("Root.__init__() called.")
        if kwargs:
            print(kwargs)
        assert not kwargs


# For test matches:
# nothing inherits from timestamp because we won't use it
# make the appropriate objects inherit from timestamp when we want it

# class TimeStamp(Root):
#     def __init__(self, **kwargs):
#
#         self.ts_start = kwargs.pop("ts_start")
#         self.ts_end = kwargs.pop("ts_end")
#         self.ts_duration = self.ts_end - self.ts_start
#
#         super(TimeStamp, self).__init__(**kwargs)


class Game(Root):
    # Data object for a Game of Ultimate.

    # # TODO: this should probably be a property of point but I don't want to do that much button pushing.
    # winds = [  # relative to starting offence
    #     u"downwind",  # the jackpot, this is winning the flip and winning the flip
    #     u"still",
    #     u"upwind",
    # ]

    def __init__(self, **kwargs):
        # Takes offence, defence, stage, division, wind, as mandatory inputs.

        # print("Game.__init__() called.")

        self.teams = kwargs.pop("teams")  # two item list: 0 = offence, 1 = defence
        self.scores = [[0, 0]]  # double nesting, want to just append the score here after each point
        self.points = []

        self.tournament = kwargs.pop("tournament")
        self.year = kwargs.pop("year")

        # self.stage = kwargs.pop("stage")  # choose from stages
        # self.wind = kwargs.pop("wind")  # relative to first possession, choose from winds
        # self.temperature = kwargs.pop("temperature")  # choose an integer value in degrees Celsius

        # TODO: build this to track how many nerds are ruined
        # self.flips = kwargs.pop("flips")

        super(Game, self).__init__(**kwargs)

    def __str__(self):
        string = "{}{}_{}_{}".format(
            self.tournament,
            self.year,
            self.teams[0].name,  # offence
            self.teams[1].name,  # defence
        )

        return string


class Point(Root):
    """Point is a length of sequences between goals."""

    # TODO: want to consider upwind/downwind at some point here too, for now it's just set at the start of game.

    def __init__(self, **kwargs):
        # print("Point.__init__() called.")

        # double nesting allows us to append new lines / a new sequence after an injury
        self.lines = [[kwargs.pop("lines")]]
        self.sequences = [[]]

        # lines and sequence are index matched - this should be useable for both to get the 'current' item
        self.set_index = 0

        # starting offence for every game = 0
        # starting offence for a point could be 1 or 0
        # will still need to remember offence as it changes
        self.starting_offence = kwargs.pop("starting_offence")
        self.offence = self.starting_offence

        super(Point, self).__init__(**kwargs)

    def current_lines(self):
        return self.lines[self.set_index]

    def current_sequence(self):
        return self.sequences[self.set_index]

    def update_seq_lin(self,lines):
        # takes in [teamA_players, teamB_players]
        # adds a new empty sequence so that the index matching works
        # and when you then work with set_index, it'll first refer to the new empty sequence
        self.lines.append(lines)
        self.sequences.append([])
        self.set_index += 1


class Team(Root):
    def __init__(self, **kwargs):
        # print("Team.__init() called.")

        self.name = kwargs.pop("name")
        self.players = kwargs.pop("players")

        # self.staff = kwargs.pop("staff")
        # self.division = kwargs.pop("division")

        super(Team, self).__init__(**kwargs)

    def __str__(self):
        return self.name


class Player(Root):
    def __init__(self, **kwargs):
        # print("Player.__init__() called.")

        self.player = kwargs.pop("name")
        self.number = kwargs.pop("number")
        self.gender = kwargs.pop("gender")

        super(Player, self).__init__(**kwargs)

    def __str__(self):
        return self.player


class Event(Root):
    # class attributes

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

        # print("Event.__init__() called.")

        self.player = kwargs.pop("player")  # will be a Player object
        self.action = kwargs.pop("action")

        # self.location = None

        super(Event, self).__init__(**kwargs)
