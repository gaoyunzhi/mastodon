#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import plain_db
import yaml
from mastodon import Mastodon
from telegram.ext import Updater
from bs4 import BeautifulSoup
import time
import mastodon_2_album

existing = plain_db.load('existing')
with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(credential['bot_token'], use_context=True)
debug_group = tele.bot.get_chat(credential['debug_group'])
tele_channel = tele.bot.get_chat(credential['tele_channel'])
timer = {}
def wait(key, sec):
    time.sleep(max(0, timer.get(key, 0) - time.time()))
    timer[key] = time.time() + sec

def getMarkdownMessage(reply_url, parent_url, content):
    return '%s [origin](%s) [source](%s)' % (content, parent_url, reply_url)

def getHtmlMessage(reply_url, parent_url, content):
    return '%s <a href=%s>origin</a> <a href=%s>source</a>' % (content, parent_url, reply_url)

def getPlainMessage(reply_url, parent_url, content):
    return '%s origin: %s source: %s' % (content, parent_url, reply_url)


def getContentText(content):
    soup = BeautifulSoup(content, 'html.parser')
    for item in soup.find_all('span', class_='h-card'):
        item.decompose()
    return soup.text

def run():
    for mastodon_name in credential['mastodon_users']:
        mastodon = Mastodon(
            access_token = 'db/%s_mastodon_secret' % mastodon_name,
            api_base_url = credential['mastodon_domain']
        )
        statuses = mastodon.account_statuses(mastodon.me().id)
        for status in statuses:
            parent_url = status.url
            for reply_status in mastodon.status_context(status.id).descendants:
                reply_url = reply_status.url
                if existing.get(reply_url):
                    continue
                content = getContentText(reply_status.content)
                message_markdown = getMarkdownMessage(reply_url, parent_url, content)
                message_html = getHtmlMessage(reply_url, parent_url, content)
                message_plain = getPlainMessage(reply_url, parent_url, content)
                wait('tele_channel', 5)
                try:
                    tele_channel.send_message(message_markdown, parse_mode='Markdown')
                except Exception as e:
                    print('mastodon_collect markdown send fail', e, reply_url)
                    try:
                        tele_channel.send_message(message_html, parse_mode='HTML')
                    except Exception as e:
                        print('mastodon_collect html send fail', e, reply_url)
                        tele_channel.send_message(message_plain)
                tele_channel.send_message()
                existing.update(reply_url, 1)
        
if __name__ == '__main__':
    run()