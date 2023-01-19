#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plain_db
import yaml
from mastodon import Mastodon
from telegram.ext import Updater

existing = plain_db.load('existing')
with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(credential['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(credential['debug_group'])
tele_channel = tele.bot.get_chat(credential['tele_channel'])

def run():
    for mastodon_name in credential['mastodon_users']:
        mastodon = Mastodon(
            access_token = 'db/%s_mastodon_secret' % mastodon_name,
            api_base_url = credential['mastodon_domain']
        )
        statuses = mastodon.account_statuses(mastodon.me().id)
        print(len(statuses))
        return # testing
        
if __name__ == '__main__':
    run()