#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: snipermonke01
"""

import requests
import os


class TelegramManager:

    def __init__(self):

        try:
            self.bot_chatID = os.environ['MVX_TELEGRAM_CHAT_ID']
            self.telegram_bot_api = os.environ['MVX_TELEGRAM_BOT_API']

        except KeyError:
            pass

    def telegram_bot_sendtext(self, message):

        send_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(
            self.telegram_bot_api, self.bot_chatID, message)

        response = requests.get(send_url)

        return response.json()


def make_query(query: str):
    """
    Get short and long positions for a given chain

    Parameters
    ----------
        query: str
            Formatted subgraph query
        is_arbritrum: bool
            Pass True to get arbitrum short and long positions
        is_avax: bool
            Pass True to get avax short and long positions
    """

    url = "https://api.thegraph.com/subgraphs/name/sdcrypt0/mvx-subgraph-core-v2"

    result = requests.post(url,
                           json={'query': query}).json()

    return result
