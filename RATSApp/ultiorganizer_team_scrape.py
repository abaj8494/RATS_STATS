#!/usr/bin/env python
# -*- coding: utf-8 -*-

# team_scrape.py

# standard library
from __future__ import print_function
import os
import sys
import codecs
import urllib2
import re

# third party
from bs4 import BeautifulSoup

# local project
import game_hierarchy


WORLDS_CHUNK = "http://scores.wugc2016.com/"


def make_soup(hyperlink):
    """Takes a hyperlink and returns a BeautifulSoup object."""

    request = urllib2.Request(hyperlink)
    response = urllib2.urlopen(request)
    return BeautifulSoup(response.read().decode("utf-8", "ignore"), "html.parser")


def find_divisions(soup):
    """Returns a list of teams and their hyperlinks for each non-Guts divisions at the tournament."""

    divisions = soup.find("div", class_="content").find_all("table")

    return [
        # divisions
        [
            division.th.string,  # division name
            # teams
            [
                [
                    [link.string, WORLDS_CHUNK + link.get("href")]
                    for link in table_row.find_all("a")
                ]
                # table rows loop
                for table_row in division.find_all("tr")
            ][1:],  # slice out division name
        ]
        # divisions loop
        for division in divisions if division.th.string != u"Guts"
    ]


# def create_team(team_links, division):
#     """Takes a list of team links and creates a Team object."""
#
#     # print(division, ", ".join("{} {}".format(link[0], link[1]) for link in team_links))
#
#     team_group = team_links[1][0]
#     name_team = team_links[0][0]
#     players_team = team_links[2][1]
#     team_games = team_links[4][1]
#     print(team_games)
#
#     team_object = game_hierarchy.Team()
#
#     print(team_object.games)
#
#     return team_object


def scrape_game():

    soup = make_soup("http://scores.wugc2016.com/?view=gameplay&game=223")
    # print(soup.prettify())

    game_headers = [
                       header.get_text()
                       for header
                       in soup.find("table", border="1", cellpadding="2", width="100%").find_all("th")
                   ]
    # print(game_headers)

    game_scores = [
                      row.find_all("td")
                      for row
                      in soup.find("table", border="1", cellpadding="2", width="100%").find_all("tr")
                  ][1:]  # slice removes headers

    # [print(score) for score in game_scores]

    game_progression = []

    for score in game_scores:

        if len(score) == 6:  # point

            # find Game Events (starting offence, timeouts) and make them separate entries into the progression
            if score[-1].string is not None:
                # print(score[-1])
                game_progression.append(score[-1])
                # TODO: find the div["class"] attribute

            # append the rest of the row to the game progression
            # print(score[:-1])

            print(score[0]["class"])
            print(score[0].string.strip())

            home_regex = "^(\d+)\s"

            game_progression.append(score[:-1])

        elif len(score) == 1:  # halftime
            game_progression.append(score)

        else:  # shouldn't get here
            raise ValueError

    game_list = []
    game_list.append(["starting offence", game_progression.pop(0).div["class"][0], [0, 0]])

    print("")
    print(game_list)

    # TODO: turn this into a gh.Game object


def main():

    # TODO: this gets the game links for each team, leaving it to do the AUS-JAP women's game
    # soup = make_soup("http://scores.wugc2016.com/?view=teams&season=WUGC16&list=allteams")
    # print(soup.prettify())
    #
    # division_tables = find_divisions(soup)
    # # print(division_tables)
    # # print(len(division_tables))
    #
    # for division in division_tables:
    #     # print(division[1])
    #     # print(len(division[1]))
    #
    #     for team_links in division[1]:
    #         # print(len(team_links))
    #         print(team_links[-1][-1])  # hyperlinks to team games
    #
    #         team_object = create_team(team_links, division[0])

    scrape_game()

    return None


if __name__ == u"__main__":
    sys.exit(main())
