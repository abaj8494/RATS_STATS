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

    # TODO: these should be set at a higher level.
    point_cap = 15
    half_at = 8
    offences = [u"home", u"guest"]

    soup = make_soup("http://scores.wugc2016.com/?view=gameplay&game=223")
    # print(soup.prettify())

    # game_headers = [
    #                    header.get_text()
    #                    for header
    #                    in soup.find("table", border="1", cellpadding="2", width="100%").find_all("th")
    #                ]
    # # print(game_headers)

    game_scores = [
                      row.find_all("td")[::-1]
                      for row
                      in soup.find("table", border="1", cellpadding="2", width="100%").find_all("tr")
                  ][1:]  # slice removes headers

    # [print(score) for score in game_scores]

    # find starting and half offences - these are stored as colours in the table for idiotic reasons.
    # TODO: work out who to ask for the actual data from Worlds - Rich?
    starting_offence = game_scores[0][0].div["class"][0]
    offences.remove(starting_offence)
    half_offence = offences[0]

    print("starting offence: {}\n"
          "half offence:     {}".format(starting_offence, half_offence))


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
