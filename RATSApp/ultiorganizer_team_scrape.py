# standard library
import sys
import pickle
import re
from urllib.request import urlopen

# third party
from bs4 import BeautifulSoup, Comment, NavigableString

# local application
import GameHierarchy


# global variables
URL_CHUNK = "http://scores.wugc2016.com/"  # gets appended to various urls
TESTING = True


def find_divisions(soup):
    """Returns the division name and its bs4.element.ResultSet table."""

    return [[[kevin.string for kevin in child.find_all("th")],  # division name
             child]  # ResultSet
            for child in soup.find(attrs={"class": "content"}).find_all("table")][1:]


def find_teams(division):
    """Returns a list of the team name, team page, and games page for each team in the division."""

    global URL_CHUNK

    return [[team.find_all("td")[0].get_text(),  # team name
              [URL_CHUNK + link.get("href") for link in team.find_all("a")][0],  # team page
              [URL_CHUNK + link.get("href") for link in team.find_all("a")][-1]]  # scores page
             for team in division.find_all("tr")[1:]]  # slicing removes header


def find_team_data(team_page):
    """Returns the team's coaching staff and player statistics."""

    global URL_CHUNK, TESTING

    if TESTING:
        team_soup = BeautifulSoup(
            open("/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/AUS_men_teamcard.htm"),
            "html.parser")
    else:
        team_webpage = urlopen(team_page)
        team_soup = BeautifulSoup(team_webpage, "html.parser")

    content_division_tables = team_soup.find(attrs={"class": "tdcontent"}).find_all("table")
    # print(content_division_tables)

    coaching_staff = [[kevin.get_text().title() for kevin in child]
                      for child in content_division_tables[0].children if type(child) is not NavigableString][1:]
    # print(coaching_staff)

    individuals_statistics = []
    for player in content_division_tables[1].find_all("tr")[1:]:
        individual_statistics = []

        for child in player.children:
            number = re.search("\d+", child.string).group(0)
            # print(number)

            try:
                player = re.search("\s(\w[\w|\s]+)", child.string).group(0).title().strip()
                # print(player)
                individual_statistics.append([number, player])
            except AttributeError:
                individual_statistics.append(number)
                continue

        individuals_statistics.append(individual_statistics)

    # [print(individual) for individual in individuals_statistics]

    return [coaching_staff, individuals_statistics]


def find_games(scores_link, team):
    """Returns an ordered list of the team's games."""

    # TODO: this is returning games without links

    global TESTING, URL_CHUNK

    washout = "\xa0"
    games = []

    if TESTING:  # open from saved webpage
        soup = BeautifulSoup(open(
            # "/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/AUS_men_scores.htm"),  # AUS Men
            "/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/FRA_men_scores.htm"),  # FRA Men
            # "/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/COD_men_scores.htm"),  # COD Men
            "html.parser")
    else:  # open the webpage
        scores_html = urlopen(scores_link)
        soup = BeautifulSoup(scores_html, "html.parser")

    days = soup.find(attrs={"class": "content"})  # bs4.element.Tag

    # loop through and get all the game information
    for descendant in days.descendants:

        if type(descendant) == Comment:
            date = descendant.strip()
            # print(date.strip())

        if descendant.name == "table":

            for child in descendant:

                cells = []

                if child.name == "tr":  # each row in the table
                    # print(child)

                    for cell in child:
                        # print(len(cell))
                        # print(cell.name)

                        if cell.name == "th":
                            stage = cell.string
                            # print(stage)

                        if cell.name == "td":

                            if len(cell.find_all("a")) > 0:  # if there is a game_hyperlink

                                for link in cell.find_all("a"):
                                    cells.append(date)
                                    cells.append(stage)

                                    baby = child.find_all("td")
                                    for embryo in baby:
                                        if embryo.string is not None and embryo.string != "-":
                                            cells.append(embryo.string)
                                            # print(embryo.string)

                                    game_hyperlink = URL_CHUNK + link.get("href")
                                    # print(game_hyperlink)
                                    cells.append(game_hyperlink)

                                game = []

                                # print("\n{}".format(cells))

                                # print(cells)
                                # print(len(cells))

                                if len(cells) > 1:  # blanks from headers
                                    # print(cells)
                                    # print("{} len: {}".format(cells, len(cells)))
                                    # print(len(cells))
                                    # print(cells[3] != washout)

                                    if cells[5] != washout and cells[6] != washout:

                                        kevins = [cell for cell in cells]
                                        # print(kevins)

                                        if cells[4] == team:  # team is first
                                            for kevin in kevins:
                                                game.append(kevin)

                                        elif cells[7] == team:  # team is second
                                            game.append(kevins[0])
                                            game.append(kevins[1])
                                            game.append(kevins[2])
                                            game.append(kevins[3])
                                            game.append(kevins[7])
                                            game.append(kevins[6])
                                            game.append(kevins[5])
                                            game.append(kevins[4])
                                            game.append(kevins[8])

                                        # print(game)
                                        games.append(game)
    # print("GAMES")
    [print(game) for game in games]
    return games


def find_game_data(team, game_hyperlink):
    """Returns a list of the player statistics table for the team, the opponent's team, and the score sequence table."""

    global TESTING

    if TESTING:  # open saved webpage
        game_soup = BeautifulSoup(open(
            "/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/AUS_men_COL.htm"), "html.parser")
    else:  # open hyperlink
        game_soup = BeautifulSoup(urlopen(game_hyperlink), "html.parser")

    game_content = game_soup.find(attrs={"class": "content"})
    soup_tables = [[cell.string for cell in table.find_all("td") if cell.string is not "Half-time"]
                   for table in game_content.find_all("table")][1:]

    # [print("\n{}".format(table)) for table in soup_tables]

    home = soup_tables[0][0]
    guest = soup_tables[2][0]

    if team == soup_tables[0][0]:
        opponent = soup_tables[2][0]
        player_statistics = [soup_tables[0][0], soup_tables[1]]
        opponent_statistics = [soup_tables[2][0], soup_tables[3]]
        spirit_scores = [soup_tables[6][-2][soup_tables[6][-2].find("(")+1:soup_tables[6][-2].find(")")].split("+"),
                         soup_tables[6][-1][soup_tables[6][-1].find("(")+1:soup_tables[6][-1].find(")")].split("+")]
    elif team == soup_tables[2][0]:
        opponent = soup_tables[0][0]
        player_statistics = [soup_tables[2][0], soup_tables[3]]
        opponent_statistics = [soup_tables[0][0], soup_tables[1]]
        spirit_scores = [soup_tables[6][-1][soup_tables[6][-1].find("(")+1:soup_tables[6][-1].find(")")].split("+"),
                         soup_tables[6][-2][soup_tables[6][-2].find("(")+1:soup_tables[6][-2].find(")")].split("+")]
    else:
        raise NameError

    point_tags = [[cell for cell in table.find_all("td") if cell.string != "Half-time"]
                  for table in game_content.find_all("table")][6]
    # print(point_tags)
    # print("/5: {}".format(len(point_tags) % 5 == 0))
    # print("/6: {}".format(len(point_tags) % 6 == 0))

    try:
        points_sequence = find_game_sequence([point_tags[a:a+6] for a in range(0, len(point_tags), 6)], team, opponent, home, guest)
    except TypeError:
        points_sequence = find_game_sequence([point_tags[a:a+5] for a in range(0, len(point_tags), 5)], team, opponent, home, guest)

    return player_statistics, opponent_statistics, points_sequence, spirit_scores


def find_game_sequence(sequence_table, team, opponent, home, guest):
    """Return the point sequence."""

    points_details = []
    for point in sequence_table:
        # print(point)
        # print(len(point))

        # print(point[0]["class"][0])

        if point[0]["class"][0] == "home":
            team_action = home
        elif point[0]["class"][0] == "guest":
            team_action = guest
        else:
            raise ValueError
        # print(team_action)

        point_details = [team_action]
        for cell in point:
            if cell.string is not None:
                point_details.append(cell.string.title().strip())
                # print(cell.string.title().strip())

        # point_details = [cell.string.title().strip() for cell in point if cell.string is not None]

        if len(point) == 6:
            if point[-1].string is not None:
                # print(point[-1].find("div")["class"][0])
                if point[-1].find("div")["class"][0] == "home":
                    point_details.append(home)
                elif point[-1].find("div")["class"][0] == "guest":
                    point_details.append(guest)

        points_details.append(point_details)

    # [print(point) for point in points_details]

    return find_point_sequence(points_details, team, opponent, home, guest)


def find_point_sequence(sequence_list, team, opponent, home, guest):
    """Return the possession sequence."""

    # TODO: timeouts
    # print("Team: {}".format(team))
    # print("Home: {}".format(home))
    # print("Away: {}".format(guest))
    # print("team==home: {}".format(team == home))
    # print("team==guest: {}".format(team == guest))

    points = []
    for point in sequence_list:
        # print(point)
        # print(len(point))

        scoring_team = point[0]
        score = point[1]

        scores = score.split(" - ")
        # print(scores)

        if team == home:
            # print("home, keep scores")
            team0_score = re.search("\d+", score).group(0)
            team1_score = re.search("\s(\d+)", score).group(0)
        elif team == guest:
            # print("away, flip scores")
            team1_score = re.search("\d+", score).group(0)
            team0_score = re.search("\s(\d+)", score).group(0)
        else:
            raise ValueError

        assist = point[2]
        goal = point[3]
        finish = point[4]
        duration = point[5]
        events = ""

        if len(point) == 8:
            events = "{} {}".format(point[6], point[7])
            # TODO: should maybe keep these separately.

        if sequence_list.index(point) == 0:
            starting_offence = point[-1]
            start = "0.00"  # TODO: storing times
            events = ""

        # halftime check
        elif re.search("\d+", sequence_list[sequence_list.index(point) - 1][1]).group(0) == 8 or \
            re.search("\s(\d+)", sequence_list[sequence_list.index(point) - 1][1]).group(0) == 8:
                starting_offence = switch_offence(sequence_list[0][-1], home, guest)
                start = int(finish) - int(duration)  # TODO: duration maths

        else:
            starting_offence = switch_offence(sequence_list[sequence_list.index(point) - 1][0], home, guest)
            start = sequence_list[sequence_list.index(point) - 1][4]

        game_possessions = [[scoring_team, [[0.00, assist, "throw", "goal", 0.00], [0.00, goal, "catch", "goal", finish]]]]
        if starting_offence is scoring_team:
            if assist == "Callahan-Goal":
                game_possessions = [[scoring_team, [[0.00, "", "", "turnover", 0.00]],
                                    switch_offence(scoring_team, home, guest), [[0.00, "", "", "turnover", 0.00]],
                                    scoring_team, [[0.00, assist, "throw", "goal", 0.00], [0.00, goal, "catch", "Callahan", finish]]]]
        else:
            game_possessions.insert(0, [switch_offence(scoring_team, home, guest), [[0.00, "", "", "turnover", 0.00]]])

        # [print(possession) for possession in game_possessions]

        points.append([team, team0_score, opponent, team1_score, game_possessions, [start, finish, duration], events])

    [print(point) for point in points]

    return points


def switch_offence(offence, home, guest):
    """Return the other team as offence."""

    if offence == home:
        return guest
    elif offence == guest:
        return home
    else:
        return "error, offence has not switched"


def main():
    """Scrapes tournament data and saves into divisions (raw) and the tournament (objects)."""

    global TESTING

    division_names = [["None", "Men"], ["None", "Women"], ["None", "Mixed"], ["Master", "Men"], ["Master", "Women"]]
    tournament_season = "WUC 2016"
    tournament_season_start = "18 June 2015"
    tournament_season_finish = "25 June 2016"
    tournament_name = "World Ultimate Championships 2016"
    tournament_url = "http://scores.wugc2016.com/?view=teams&season=WUGC16&list=allteams"
    tournament_start = "18 June 2016"
    tournament_finish = "25 June 2016"
    tournament_location = "London, England"
    tournament_points_cap = 15
    tournament_time_cap = 100


    """Main entry point for script."""

    if TESTING:  # open saved webpage
        soup = BeautifulSoup(open(
            "/Users/awoo5332/Google Drive/Coding/Python/ultimate_analysis/wugc2016/wugc2016_allteams.htm"),
            "html.parser")

    else:  # scrape from the internet
        hyperlink = 'http://scores.wugc2016.com/?view=teams&season=WUGC16&list=allteams'
        page_html = urlopen(hyperlink)
        soup = BeautifulSoup(page_html, "html.parser")

    divisions = find_divisions(soup)  # Name, Table
    divisions_teams_games_data = []

    for division in divisions:
        division_name = division[0][0]
        if division_name == "Men":
            division_age = "None"
            division_gender = "Men"
        elif division_name == "Women":
            division_age = "None"
            division_gender = "Women"
        elif division_name == "Mixed":
            division_age = "None"
            division_gender = "Mixed"
        elif division_name == "Master Men":
            division_age = "Master"
            division_gender = "Men"
        elif division_name == "Master Women":
            division_age = "Master"
            division_gender = "Women"

        print("##### DIVISION: {} #####".format(division_name))

        division_teams = find_teams(division[1])

        teams_games_data = []

        for team in division_teams:
            team_name = team[0]
            print("@@@ TEAM: {} @@@".format(team_name))

            games = []

            team_page = team[1]
            team_data = find_team_data(team_page)
            print("** STAFF **")
            # print(team_data)

            team_scores = team[2]
            # print(team_scores)
            game_details = find_games(team_scores, team_name)
            # print(game_details)

            for game in game_details:
                print("########################################### Game ##########################################")
                # print("{}: {}".format(team_name, game[-1]))
                print(game)
                gamedata = find_game_data(team_name, game[-1])
                games.append([game[:-1], gamedata])

            if len(game_details) > 0:
                teams_games_data.append([team_name, team_data, games])
                print("%% Team information appended %%")

            elif len(game_details) == 0:
                print("%% No games, team not appended %%")

        sys.setrecursionlimit(10000)
        pickle.dump([division_age, division_gender, teams_games_data],
                    open("{}_{}_data.p".format(division_age, division_gender), "wb"))
        print("Division scrape saved.")

        divisions_teams_games_data.append([division_age, division_gender, teams_games_data])

    division_objects = []

    for division_name in division_names:

        print("Loading {} {} data ...".format(division_name[0], division_name[1]))
        division_teams_games_data = pickle.load(
            open("{}_{}_data.p".format(division_name[0], division_name[1]), "rb"))

        division_age = division_teams_games_data[0]
        division_gender = division_teams_games_data[1]
        teams_games_data = division_teams_games_data[2]
        # print(teams_games_data)

        division_object = GameHierarchy.Division(
            season=tournament_season,
            season_start=tournament_season_start,
            season_finish=tournament_season_finish,
            tournaments=[],
            tournament=tournament_name,
            tournament_start=tournament_start,
            tournament_finish=tournament_finish,
            location=tournament_location,
            points_cap=tournament_points_cap,
            time_cap=tournament_time_cap,
            divisions=[],
            division="{} {}".format(division_age, division_gender),
            age=division_age,
            gender=division_gender,
            teams=[GameHierarchy.Team(
                group=team[0][:3],
                team=team[0][4:],
                division="{} {}".format(division_age, division_gender),
                age=division_age,
                gender=division_gender,
                captains=team[1][0][-1][-1].split(", "),
                coaches=team[1][0][0][-1].split(", "),
                players=[GameHierarchy.Player(
                    group=team[0][:3],
                    team=team[0][4:],
                    division="{} {}".format(division_age, division_gender),
                    age=division_age,
                    gender=division_gender,
                    number=player[0][0],
                    player=player[0][1]
                ) for player in team[1][-1]],
                games=[GameHierarchy.Game(
                    date=game[0][0],
                    stage=game[0][1],
                    time=game[0][2],
                    field=game[0][3],
                    team0=game[0][4],
                    score0=int(game[0][5]),
                    score1=int(game[0][6]),
                    team1=game[0][7],
                    timeouts0=0,
                    timeouts1=0,
                    points=[GameHierarchy.Point(
                        team0=point[0],
                        score0=point[1],
                        team1=point[2],
                        score1=point[3],
                        possessions=[GameHierarchy.Possession(
                            possession_team=possession[0],
                            stalls=[GameHierarchy.Stall(
                                stall_player=stall[1],
                                action=stall[2],
                                outcome=stall[3]
                            ) for stall in possession[1]]
                        ) for possession in point[4]],
                        start=point[5][0],
                        finish=point[5][1],
                        duration=point[5][2],
                        events=point[6]
                    ) for point in game[1][2]],
                    spirit0=game[1][3][0],
                    spirit1=game[1][3][1]
                ) for game in team[2]]
            ) for team in teams_games_data]
        )
        # print(division_object)
        # [print("{} {}".format(a.group, a.team)) for a in division_object.teams]
        # print(division_object.teams)

        print(division_object)
        division_objects.append(division_object)
        print("Division appended.")

        # for sporting_team in division_object.teams:
        #     print("{} {}".format(sporting_team.group, sporting_team.team))
        #
        #     for game in sporting_team.games:
        #         print(game)

        #Rob and Andy are fuckinnnn ratttssssss hahahahahahahhaa

    wuc_2016 = GameHierarchy.Tournament(
        season=tournament_season, season_start=tournament_season_start, season_finish=tournament_season_finish,
        tournaments=[], tournament=tournament_name, tournament_start=tournament_start,
        tournament_finish=tournament_finish, location=tournament_location, points_cap=tournament_points_cap,
        time_cap=tournament_time_cap, divisions=[a for a in division_objects], url=tournament_url
    )
    print(wuc_2016)

    sys.setrecursionlimit(10000)
    pickle.dump(wuc_2016, open("wuc_2016_data.p", "wb"))
    print("Tournament saved.")


if __name__ == '__main__':
    sys.exit(main())

