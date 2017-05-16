# !/usr/bin/env python
# -*- coding: utf-8 -*-

# open a game file
# read through points
# read through sequences
# read through possessions
# read through discs

# spit out numbers for both teams and each player in each team.
# TAG'd
# MON'd

# retention == passes completed per pass attempted  # TODO: individual player stats, different for shot takers
# efficiency == goals scored per possession  # TODO: where is the win line? above what percentage?
# conversions == goals scored per point played  # TODO: what lines are most efficient at conversions

# imports

# standard library
import sys
import pickle

# local project
import raw_game_hierarchy as rgh

# TODO: work out how to extend classes in RGH


class Root():
    """
    Wrapper class for debugging.
    """

    def __init__(self, **kwargs):
        """
        Raises an assertion error if any unexpected kwargs exist on initialisation.
        """

        if kwargs:
            print(kwargs)  # Andy - if these exist we need to work out why
            print("Root.__init__() called.")

        assert not kwargs


class AnalysedTeam(Root):
    """storage unit for Team level statistics for a Game object."""

    def __init__(self, **kwargs):
        """
        Parameters:
             team_name, team_coaches, team_players, team_opponent, 
             as mandatory arguments.
        """

        """
        LIVE RATS: statistics to pull out during a game
        """

        # Game Descriptors
        self.team_name = kwargs.pop("team_name")  # string
        self.team_coaches = kwargs.pop("team_coaches")  # list of Coach objects
        self.team_players = kwargs.pop("team_players")  # list of Player objects
        self.team_opponent = kwargs.pop("team_opponent")  # string - matches team.name

        # Points
        self.team_points = 0  # count
        self.team_offences = 0  # count of points on offence
        self.team_defences = 0  # count of points on defence

        # Possessions
        self.team_offensive_possessions = 0  # count
        self.team_defensive_possessions = 0  # count

        # Touches
        self.team_discs = 0
        self.team_completions = 0
        self.team_turnovers = 0
        # TODO: check that completions + turnovers == discs
        self.completion_rate = 0.00

        # Offence
        self.team_offensive_holds = []  # count
        self.team_offensive_breaks = []  # count
        self.team_offensive_retention = 0.00  # percentage
        self.team_offensive_efficiency = 0.00

        # Defence
        self.team_defensive_holds = []  # count
        self.team_defensive_breaks = []  # count
        self.team_offensive_conversions = 0.00  # percentage
        self.team_defensive_efficiency = 0.00

        # Goals
        self.team_goals = []  # list of player pairs, can count len() for the score

        # Defences
        self.team_defences = []  # list of players who created turnovers, should include the point index

        """
        DEAD RATS: statistics to pull out after a game
        """

        # self.team_offensive_structures = []  # TODO: list of initial play calls, done after the Game
        # self.team_defensive_structures = []  # TODO: list of defensive calls, done after the Game
        # TODO: offensive_points + defensive_points == points_played

        # TODO: on/off numbers, player valuations

        super(AnalysedTeam, self).__init__(**kwargs)


class AnalysedPlayer(Root):
    """
    storage unit for Player level statistics for a Game object.
    """

    def __init__(self, **kwargs):
        """
        Parameters:
             takes player_name, player_number, player_gender
             as mandatory inputs.
        """

        # Game Descriptors
        self.player_name = kwargs.pop("player_name")
        self.player_number = kwargs.pop("player_number")
        self.player_gender = kwargs.pop("player_gender")

        # Points
        self.player_points = 0
        self.player_offences = 0
        self.player_defences = 0

        # Possessions - these get compared to TeamPossessions
        self.player_offensive_possessions = 0  # TeamPossessions which include the player, want a percentage eventually
        self.player_defensive_possessions = 0  # TeamPossessions which include the player, want a percentage eventually

        # PlayerDiscs
        # Offence
        self.player_touches = 0
        self.player_completions = 0
        self.player_turnovers = 0
        self.player_assists = 0
        self.player_goals = 0
        self.player_completion_rate = 0.00

        # Defence
        self.player_defences = 0
        # TODO: completion_rate = completions / touches

        super(AnalysedPlayer, self).__init__(**kwargs)


def load_game(file_path):
    """
    Open a Game pickle file.
    """

    game = pickle.load(open(file_path, 'rb'))
    return game


def run_player_analysis(player, game):

    player_statistics = Player(
        name=player.player_name,
        number=player.player_number,
        gender=player.player_gender,
    )

    # TODO: this is broken because of how RGH is structured so I'm gonna have to change something there

    # player_statistics = AnalysedPlayer(
    #     name=player.name,
    #     number=player.number,
    #     gender=player.gender,
    # )

    for point in game.points:  # loop over points

        for sequence in point.sequences:  # loop over sequences

            # if the player is not in this sequence
            if player not in sequence.lines[0] and player not in sequence.lines[1]:  # will this object comparison work
                # TODO: Andy - it should
                continue  # go to the next one

            player_statistics.player_points += 1

            for i in range(0, len(sequence.events)):

                event = sequence.events[i]

                if event.player == player:

                    # single-check events
                    player_statistics.player_touches+=1

                    if event.action == 'goal':
                        player_statistics.player_goals += 1

                    if i < len(sequence.events)-1: # dont go past the end - better safe than sorry
                        # print(str(i)+'#'+str(len(sequence.events)))

                        if sequence.events[i+1].action == 'goal':
                            player_statistics.player_assists += 1

                    if event.action == 'block':
                        player_statistics.player_defences += 1

                    if event.action in rgh.Event.turnover_actions:
                        player_statistics.player_turnovers += 1

            # calculated stats - these numbers to be run after reading over the whole game (for a player)
            if player_statistics.player_touches != 0:
                player_statistics.completion_rate = player_statistics.player_turnovers / player_statistics.player_touches

            else:
                player_statistics.completion_rate = 1.00

    return player_statistics


def point_progressions(game):
    """Points in the Game."""

    return [point for point in game.points]


def sequence_progressions(game):
    """Sequences in a Point"""

    return [[sequence for sequence in point.sequences] for point in game.points]


def possession_progression(analysed_game):
    """TeamPossessions in a Sequence."""

    starting_offence_possessions = [[]]
    starting_defence_possessions = [[]]

    for point in analysed_game.points:
        # print(point)
        print("\n")

        for sequence in point.sequences:
            print("starting offence: {}".format(sequence.offence))

            print("sequence length: {}".format(len(sequence.events)))
            for event in sequence.events:
                print(event)

                # TODO: Andy - this needs to check Australia or Japan
                if event.action != u"goal":

                    if event.action not in rgh.Event.turnover_actions:

                        if event.player in analysed_game.teams[0]:  # starting offence
                            starting_offence_possessions[0].append(event)
                        elif event.player in analysed_game.teams[1]:
                            starting_defence_possessions[0].append(event)
                        else:
                            raise ValueError  # something has gone wrong with the team check


def discs_progression():
    """PlayerDiscs in a TeamPossession"""


def main():
    """"""

    analysed_game = load_game('Test Match Series2017_Melbourne Juggernaut_Brunch Smashed_final.p')

    # print(type(analysed_game))
    # print(analysed_game.points)

    for team in analysed_game.teams:

        for player in team.players:
            this_player = run_player_analysis(player,analysed_game)
            print('Name: ' + str(this_player.name))
            print('Touches: ' + str(this_player.touches))
            print('Goals: ' + str(this_player.goals))
            print('Assists: ' + str(this_player.assists))
            print('Blocks: ' + str(this_player.blocks))
            print('Points Played: ' + str(this_player.points_played))
            print('__________________________________________')

    possession_progression(analysed_game)


if __name__ == '__main__':
    sys.exit(main())
