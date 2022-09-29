#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 15:09:15 2022

@author: snipermonke01
"""

import time
from urllib.parse import quote_plus

from utils import TelegramManager, make_query


class MVXOpenInterest(TelegramManager):

    def __init__(self):

        super().__init__()

        self.subgraph_query = """{tradingStats(
                                  first: 10
                                  orderBy: timestamp
                                  orderDirection: desc
                                  where: { period: "hourly",
                                          timestamp_gte: 1664199496,
                                          timestamp_lte:
                              """ + str(int(time.time())) + """})
                                {
                                  timestamp
                                  longOpenInterest
                                  shortOpenInterest
                                }
                                }
            """

    def get_open_interest(self):

        raw_data = make_query(self.subgraph_query)

        latest_raw_oi = raw_data['data']['tradingStats'][0]
        previous_raw_oi = raw_data['data']['tradingStats'][1]

        latest_long_open_interest, latest_short_open_interest = self._process_raw_oi(
            latest_raw_oi)

        previous_long_open_interest, previous_short_open_interest = self._process_raw_oi(
            previous_raw_oi)

        open_interest_stats = {
            'latest_long_open_interest': latest_long_open_interest,
            'latest_short_open_interest': latest_short_open_interest,
            'latest_time': latest_raw_oi['timestamp'],
            'previous_long_open_interest': previous_long_open_interest,
            'previous_short_open_interest': previous_short_open_interest,
            'previous_time': previous_raw_oi['timestamp']
        }

        message = self._get_telegram_message(open_interest_stats)

        return message

    def _process_raw_oi(self, data):

        long_open_interest = int(data['longOpenInterest']) / \
            1000000000000000000000000000000
        short_open_interest = int(data['shortOpenInterest']) / \
            1000000000000000000000000000000

        return long_open_interest, short_open_interest

    def _get_telegram_message(self, open_interest_stats):

        long_difference = self._get_open_interest_changes(open_interest_stats['latest_long_open_interest'],
                                                          open_interest_stats['previous_long_open_interest'])

        short_difference = self._get_open_interest_changes(open_interest_stats['latest_short_open_interest'],
                                                           open_interest_stats['previous_short_open_interest'])

        header = "MVX Open Interest Stats"
        body_long = "Long Positions: ${:,.2f}\n({} vs previous)".format(
            open_interest_stats['latest_long_open_interest'],
            long_difference)
        body_short = "Short Positions: ${:,.2f}\n({} vs previous)".format(
            open_interest_stats['latest_short_open_interest'],
            short_difference)

        sentiment_body = self._get_oi_descripter(open_interest_stats['latest_long_open_interest'],
                                                 open_interest_stats['latest_short_open_interest'])

        message = "{}\n\n{}\n{}\n\n{}".format(header,
                                              body_long,
                                              body_short,
                                              sentiment_body)
        print(message)
        self.telegram_bot_sendtext(message)

    def _get_open_interest_changes(self, latest, previous):

        if latest > previous:

            difference = "\U0001F4C8 ${:,.2f}".format(abs(latest-previous))

        elif latest < previous:

            difference = "\U0001F4C9 ${:,.2f}".format(abs(latest-previous))

        else:

            difference = 'No Change'

        return difference

    def _get_open_interest_changes(self, latest, previous):

        if latest > previous:

            difference = "\U0001F4C8 ${:,.2f}".format(abs(latest-previous))

        elif latest < previous:

            difference = "\U0001F4C9 ${:,.2f}".format(abs(latest-previous))

        else:

            difference = 'No Change'

        return difference

    @staticmethod
    def _get_oi_descripter(long_oi: float, short_oi: float):
        """
        Given a chain, long & short values make formatted message to send to telegram
        Parameters
        ----------
            long_oi: float
                Value of long positions
            short_oi: float
                Value of short positions
        """

        oi_difference = abs(long_oi-short_oi)
        total_oi = long_oi + short_oi
        diff_percent_of_oi = (oi_difference/total_oi)*100

        if long_oi > short_oi:
            direction = 'bullish'
            direction_emoji = '\U0001F402'
            oi_diff_description = '${:,.2f} more longs than shorts ({:.2f}% of oi)'.format(oi_difference,
                                                                                           diff_percent_of_oi)
        elif long_oi < short_oi:
            direction = 'bearish'
            direction_emoji = '\U0001F9F8'
            oi_diff_description = '${:,.2f} more shorts than longs ({:.2f}% of oi)'.format(oi_difference,
                                                                                           diff_percent_of_oi)

        if diff_percent_of_oi <= 5:
            direction = 'neutral'
            descripter = ""
            direction_emoji = '\U0001F610'
        elif 5 < diff_percent_of_oi <= 10:
            descripter = 'slightly '
        elif 10 < diff_percent_of_oi <= 25:
            descripter = 'pretty '
        elif 25 < diff_percent_of_oi <= 40:
            descripter = 'very '
        elif diff_percent_of_oi > 40:
            descripter = 'giga '

        description = "{} Sentiment is {}{} {}".format(direction_emoji,
                                                       descripter,
                                                       direction,
                                                       direction_emoji)
        return "{}\n{}".format(description,
                               oi_diff_description)


if __name__ == "__main__":

    MVXOpenInterest().get_open_interest()

