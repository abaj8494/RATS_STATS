#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes an Ultimate Central Tournament url and extracts team lists for each division.
"""

# imports
# standard library
from __future__ import print_function
import os
import sys
import codecs
import urllib2

# third party
from bs4 import BeautifulSoup

# local
import game_hierarchy as gh

# TODO: Division names are saved as user inputs because there is no Goddess. Need to build a regex to handle that.
# TODO: entry form is now number|gender|name


def get_divisions(soup):
    """Returns a list of all tournament divisions."""

    # print(soup)

    division_menu = soup.find("select", id="division").find_all("option")  # find the division select menu
    all_divisions = [option.string for option in division_menu if option.string != u"All Divisions"]

    print(all_divisions)

    return all_divisions


def load_division(tournament_url, division):
    """Reloads the tournament page with the teams in the division and returns the page soup."""

    division_url = tournament_url + u"/teams/division/" + division  # division hyperlink
    
    request = urllib2.Request(division_url)
    response = urllib2.urlopen(request)

    division_soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    # print(division_soup)

    return division_soup


def get_team_hyperlinks(division_soup, url_base):
    """Returns a dictionary with the keys as team names and the values as hyperlinks to their UC roster webpages."""

    # TODO: include team numbers with names, captains, coaches, additional

    team_hyperlinks = {
        team_link.find("h3").string.title(): url_base + team_link.get("href") + u"/roster"
        for team in division_soup.find_all("div", class_="span4 media-item-wrapper spacer1 ")
        for team_link in team.find_all("a", class_="media-item-tile media-item-tile-normal media-item-tile-cover")
    }
    print(team_hyperlinks)

    return team_hyperlinks


def load_team(team_url):
    """Loads the team page and returns the page soup."""

    request = urllib2.Request(team_url)
    response = urllib2.urlopen(request)

    team_soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    # print(team_soup)

    return team_soup


def load_team_tournament(team_url, division_integer):
    """loads the team page with the tournament roster and returns the page soup."""

    team_tournament_url = team_url + u"?division=" + unicode(division_integer)
    print(team_tournament_url)

    request = urllib2.Request(team_tournament_url)
    response = urllib2.urlopen(request)

    team_tournament_soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")
    # print(team_tournament_soup)

    return team_tournament_soup


def select_event(team_soup, tournament_name, division):
    """Selects the event, reloads the page, and returns the page soup."""

    event_menu = team_soup.find_all("form")[-1]

    division_integer = u""
    # TODO: clean up how division_integer is set

    for event in event_menu.find_all("option"):

        # print(type(event.string.strip()))
        # print(event.string.strip())
        # print(event["value"])
        # print(event.string)

        tournament_event = u"{} ({})".format(tournament_name.title(), division)
        # print(type(tournament_event))
        # print(tournament_event)

        # print(event.string.strip() == tournament_event)
        # print(type(event["value"]))
        # print(event["value"])

        if event.string.strip() == tournament_event:

            division_integer = event["value"]
            # print(division_integer)

    return division_integer


def scrape_team(team_tournament_soup, url_base):
    """scrapes team data from the roster page and returns it as [specify this]."""

    # TODO: this

    possible_headers = u"Event", u"Coaches", u"Captains", u"Men", u"Women", u"Additional"

    team_headers = team_tournament_soup.find("main", id="content").find_all("h4")
    team_personnel = team_tournament_soup.find_all("div", class_="row-fluid")[0:-1] # slices off some advertising
    # print(team_personnel)

    for row in team_personnel:
        print(row)
        print("\n")


    for header in team_headers:
        print("\n")
        # print(header.string)
        # print(header.string in possible_headers)
        # captains only listed once

        header_name = header.string.strip()

        # TODO: this should maybe check that the right event is selected, leaving for now
        if header_name == u"Event":
            print(header_name)

            for sibling in header.next_siblings:

                if sibling.name == u"form":

                    # print(sibling)
                    # print(sibling.option)
                    # print(type(sibling))
                    # print(len(sibling))

                    for option in sibling.find_all("option"):
                        # print(option.string.strip())
                        pass

                    # print(sibling.find_all("option"))
                    # break

        if header_name == u"Coaches":
            # print(type(header_name))
            # print(len(header_name))
            print(header_name)

            # TODO: there is a better way to pull this but I haven't found it yet, applies to all of this section
            coaches = header.next_sibling.next_sibling
            # print(coaches)
            # print(len(coaches))
            # print(type(coaches))

            # TODO: turn this into a list comprehension
            # coach_list = [
            #     [coach_name.string for coach_name in coaches.find_all("h3")],
            #     [url_base + coach.get("href") for coach in coaches.find_all("a")],
            #     [
            #         [span.string for span in badge.find_all("span")]
            #         for badge in coaches.find_all(attrs={"class": "badge-line"})
            #     ]
            # ]

            # [print(coach) for coach in coach_list]
            # print(coach_list)

            coach_names = [
                u" ".join(coach_name.string.decode("utf-8").split())
                for coach_name in coaches.find_all("h3")
            ]
            # print(coach_names)

            coach_links = [url_base + coach.get("href") for coach in coaches.find_all("a")]
            # print(coach_links)

            coach_roles = [
                [span.string.decode("utf-8") for span in badge.find_all("span")]
                for badge in coaches.find_all(attrs={"class": "badge-line"})
            ]
            # print(coach_roles)

            coach_genders = []

            for link in coach_links:
                try:
                    coach_genders.append(scrape_gender(link))
                except urllib2.HTTPError:
                    coach_genders.append("N/A")
            # print(coach_genders)

            for a in range(0, len(coach_names)):
                # print(coach_names[a])
                # [print(coach_role) for coach_role in coach_roles[a]]
                # print(coach_genders[a])

                coach_object = gh.Staff(
                    staff=coach_names[a],
                    roles=coach_roles[a],
                    gender=coach_genders[a]
                )
                print(coach_object)

        if header_name == u"Captains":
            print(header_name)

            # TODO: getting a unicode error here
            # captains = header.next_sibling.next_sibling
            # # print(captains)
            #
            # captain_names = [
            #     u" ".join(captain_name.string.decode("utf-8").split())
            #     for captain_name in captains.find_all("h3")
            # ]
            # # print(captain_names)
            #
            # captain_links = [url_base + captain.get("href") for captain in captains.find_all("a")]
            # # print(captain_links)
            #
            # captain_roles = [
            #     [span.string.decode("utf-8") for span in badge.find_all("span")]
            #     for badge in captains.find_all(attrs={"class": "badge-line"})
            # ]
            # # print(captain_roles)
            #
            # captain_numbers = [
            #     badge.string.decode("utf-8").strip()[1::]
            #     for badge in captains.find_all(attrs={"class": "align-right small"})
            # ]
            # # TODO: not sure if I need to convert these to ints
            # # print(captain_numbers)
            #
            # captain_genders = []
            #
            # for link in captain_links:
            #     try:
            #         captain_genders.append(scrape_gender(link))
            #     except urllib2.HTTPError:
            #         captain_genders.append("N/A")
            #
            # for a in range(0, len(captain_names)):
            #     player_object = gh.Player(
            #         player=captain_names[a],
            #         roles=captain_roles[a],
            #         gender=captain_genders[a],
            #         number=captain_numbers[a],
            #     )
            #     print(player_object)

        if header_name == u"Men":
            print(header_name)

            # TODO: this only pulls one row of the table
            men = header.next_sibling.next_sibling
            # print(men.name)

            men_names = [u" ".join(men_name.string.title().decode("utf-8").split()) for men_name in men.find_all("h3")]
            # print(men_names)

            men_links = [url_base + man.get("href") for man in men.find_all("a")]
            # print(men_links)

            men_roles = ["N/A" for name in men_names]
            # print(men_roles)

            men_numbers = [
                badge.string.decode("utf-8").strip()[1::]
                for badge in men.find_all(attrs={"class": "align-right small"})
            ]
            # print(men_numbers)

            men_genders = [u"Man/Boy" for name in men_names]

            # for link in men_links:
            #     try:
            #         men_genders.append(scrape_gender(link))
            #     except urllib2.HTTPError:
            #         men_genders.append("N/A")
            #
            # print(len(men_genders))

            for a in range(0, len(men_names)):
                player_object = gh.Player(
                    player=men_names[a],
                    roles=men_roles[a],
                    gender=men_genders[a],
                    number=men_numbers[a],
                )
                print(player_object)

        if header_name == u"Women":
            print(header_name)

            # TODO: this only pulls one row of the table
            women = header.next_sibling.next_sibling
            # print(women.name)
            # print(women)
            print("\n")

            # print(team_tournament_soup.find_all("div", class_="row-fluid"))

            women_names = [
                u" ".join(women_name.string.title().decode("utf-8").split())
                for women_name in women.find_all("h3")
            ]
            # print(women_names)

            women_links = [url_base + woman.get("href") for woman in women.find_all("a")]
            # print(women_links)

            women_roles = [u"N/A" for name in women_names]
            # print(women_roles)

            women_numbers = [
                badge.string.decode("utf-8").strip()[1::]
                for badge in women.find_all(attrs={"class": "align-right small"})
            ]
            # print(women_numbers)

            women_genders = [u"Woman/Girl" for name in women_names]

            # for link in women_links:
            #     try:
            #         women_genders.append(scrape_gender(link))
            #     except urllib2.HTTPError:
            #         women_genders.append("N/A")
            #
            # print(len(women_genders))

            for a in range(0, len(women_names)):
                player_object = gh.Player(
                    player=women_names[a],
                    roles=women_roles[a],
                    gender=women_genders[a],
                    number=women_numbers[a],
                )
                print(player_object)

        if header_name == u"Additional":
            print(header_name)

            # # TODO: there is a better way to pull this but I haven't found it yet, applies to all of this section
            # additionals = header.next_sibling.next_sibling
            #
            # # TODO: turn this into a list comprehension
            # # coach_list = [
            # #     [coach_name.string for coach_name in coaches.find_all("h3")],
            # #     [url_base + coach.get("href") for coach in coaches.find_all("a")],
            # #     [
            # #         [span.string for span in badge.find_all("span")]
            # #         for badge in coaches.find_all(attrs={"class": "badge-line"})
            # #     ]
            # # ]
            #
            # # [print(coach) for coach in coach_list]
            # # print(coach_list)
            #
            # additional_names = [
            #     u" ".join(additional_name.string.decode("utf-8").split())
            #     for additional_name in additionals.find_all("h3")
            # ]
            # # print(additional_names)
            #
            # # TODO: getting an error if there's no webpage, which means it can't find the gender
            # additional_links = [url_base + additional.get("href") for additional in additionals.find_all("a")]
            # # print(additional_links)
            #
            # additional_roles = [
            #     [span.string.decode("utf-8") for span in badge.find_all("span")]
            #     for badge in additionals.find_all(attrs={"class": "badge-line"})
            # ]
            # # print(additional_roles)
            #
            # additional_genders = []
            #
            # for link in additional_links:
            #     try:
            #         additional_genders.append(scrape_gender(link))
            #     except urllib2.HTTPError:
            #         additional_genders.append("N/A")
            # # print(additional_genders)
            #
            # for a in range(0, len(additional_names)):
            #     additional_object = gh.Staff(
            #         staff=additional_names[a],
            #         roles=additional_roles[a],
            #         gender=additional_genders[a])
            #     print(additional_object)

    return


def scrape_gender(person_url):
    """takes a person page and returns their gender."""

    # TODO: this needs a 401 exception

    request = urllib2.Request(person_url)
    response = urllib2.urlopen(request)

    coach_soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    return coach_soup.find("dd").string.decode("utf-8")


def write_team_text_file(tournament_abbreviation, division, team_entry):
    """Takes a tuple of a team and its players and writes it to a text file for the app.."""

    # TODO: save these to Google Drive in app.
    # TODO: we're importing text files but we could just be piping it to the program

    text_string = u"team:{}".format(team_entry[0]) + "\nplayers:" + ", ".join(team_entry[1]) + "\n"

    print(text_string)

    file_path = os.path.join(
        os.getcwd(),  # working directory
        tournament_abbreviation,  # tournament directory
        division,
        u"{}.txt".format(team_entry[0].replace(" ", ""))  # team file
    )
    print(file_path)

    with codecs.open(file_path, mode="w+", encoding="utf-8") as text_file:
        text_file.write(text_string)

    return text_string


def main():
    """Takes a tournament link and returns a list of teams and their players in each division."""

    tournament_url = unicode(raw_input(u"Enter Tournament hyperlink: "))

    url_base = tournament_url.split("/")[0] + "//" + tournament_url.split("/")[1] + tournament_url.split("/")[2]
    print("\n")
    print(url_base)

    tournament_abbreviation = tournament_url.split("/")[-1]
    tournament_name = u" ".join(tournament_abbreviation.split("-"))
    # tournament_name = tournament_abbreviation.join(tournament_abbreviation, " ")
    print(u"Tournament name: {}".format(tournament_name.title()))

    print(u"Tournament abbreviation: {}".format(tournament_abbreviation))

    # create tournament directory
    if not os.path.exists(os.path.join(os.getcwd(), tournament_abbreviation)):
        os.makedirs(os.path.join(os.getcwd(), tournament_abbreviation))

    # open the web page
    request = urllib2.Request(tournament_url + u"/teams")
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")

    # print(soup)

    # find the divisions in the tournament
    divisions = get_divisions(soup)

    # for each tournament division
    for division in divisions:

        # if there isn't a directory for this division
        if not os.path.exists(os.path.join(os.getcwd(), tournament_abbreviation, division)):
            # make the directory
            os.makedirs(os.path.join(os.getcwd(), tournament_abbreviation, division))

        print(u"Division: {}".format(division))

        # load the web page again with the division
        division_soup = load_division(tournament_url, division)

        # get the team hyperlinks for each team in the division
        division_teams = get_team_hyperlinks(division_soup, url_base)

        for team, team_link in division_teams.iteritems():
            #
            # print(team)
            # print(team_link)

            team_soup = load_team(team_link)
            # print("\n")

            division_integer = select_event(team_soup, tournament_name, division)
            # print(division_integer)

            tournament_roster = load_team_tournament(team_link, division_integer)

            # print(tournament_roster.find("main", id="content"))

            # TODO: come back here, now loads the team roster for the specified tournament, need to scrape personnel

            team_object = scrape_team(tournament_roster, url_base)

            break # for debugging, exits the loop after one iteration

            # write_team_text_file(tournament_abbreviation, division, team)

    print(u"Team lists saved!")


if __name__ == '__main__':
    sys.exit(main())
