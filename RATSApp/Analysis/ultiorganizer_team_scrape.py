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

    # this is the main table I'm interested in
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
          "half offence:     {}\n".format(starting_offence, half_offence))

    game_progression = [[starting_offence, 0.00, 0.00]]

    for row in game_scores:

        if len(row) == 1:  # halftime
            pass

        elif len(row) == 6:  # an actual row
            # print("\n{}".format(row))

            # timeout check
            if row[0].string is not None:
                # print(row[0])

                if row[5]:
                    # print(row[5])
                    pass
            else:
                # print(row)
                pass

        else:
            raise ValueError

    # pull is up at 0.00
    # zero index is who scored
    # first index is the point duration
    # second index is the game time

    for row in game_scores:

        if len(row) == 1:
            game_progression.append(["Halftime", game_progression[-1][-1]])

        elif len(row) == 6:
            print(row)
            game_progression.append(
                [
                row[5].string,
                float(row[1].string),
                float(row[2].string)
                ]
            )  # home or guest

        else:
            raise ValueError

    for time_line in game_progression:
        print(time_line)

    for time in game_progression:
        print(time[-1])


def main():

    # TODO: this gets the game links for each team, leaving it to do the AUS-JAP women's game

    scrape_game()

    return None


if __name__ == u"__main__":
    sys.exit(main())
