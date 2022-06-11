#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twython import Twython, TwythonError
import feedparser
import csv
import datetime
import os
import re
import sys
import time
from datetime import date
from mastodon import Mastodon
import requests
import json
from discord_webhook import DiscordWebhook
import auth
import opengraph

class Settings:
	FeedUrl = "https://tarnkappe.info/feed"
	PostedUrlsOutputFile = "/root/twitter/posted-urls.log"


def compose_message(rss_item, with_cats):
	"""Compose a tweet from title, link, and description, and then return the final tweet message."""
	title, link, description = rss_item["title"], rss_item["link"], rss_item["description"]
	tags = [t.term.replace(" ", "").replace("-", "").replace(".", "").replace("&", "").replace(":", "").replace(":", "").replace("/", " #").replace("(", "").replace(")", "").replace("$", "").replace("#", "") for t in rss_item.get('tags', [])]
	categories_string = " #".join(tags)
	categories_string = "#" + categories_string
	message = "📬 " + shorten_text(title, maxlength=240) + "\n"
	if with_cats:
		message += str(categories_string) + " "
	message += link
	return message

def shorten_text(text, maxlength):
	"""Truncate text and append three dots (...) at the end if length exceeds maxlength chars."""
	return (text[:maxlength] + '...') if len(text) > maxlength else text

def post_tweet(message, auth):
	"""Post tweet message to account."""
	try:
		twitter = Twython(auth.ConsumerKey, auth.ConsumerSecret, auth.AccessToken, auth.AccessTokenSecret)
		twitter.update_status(status = message)
	except TwythonError as e:
		print(e)

def post_telegram(message):
	params = {"chat_id": auth.TelegramAuth.ChatID, "text": message}
	url = f"https://api.telegram.org/bot{auth.TelegramAuth.Token}/sendMessage"
	requests.post(url, params=params)

def post_toot(message):
	try:
		mastodon = Mastodon(auth.MastodonAuth)
		mastodon.toot(message)
	except mastodon as e:
		print(e)

def post_signal(message):
	data = {"message": message, "number": "+4915156859153", "recipients": [ ]}
	with open("/root/Signal/rss/numbers.txt") as file:
		for line in file:
			data['recipients'].append(line.rstrip())
	requests.post('http://127.0.0.1:8120/v2/send/', timeout=300, json=data)

def post_discord(message):
	webhook = DiscordWebhook(url='https://discord.com/api/webhooks/' + auth.DiscordAuth.webhook, content=message)
	response = webhook.execute()

def read_rss_and_tweet(url):
	"""Read RSS and post tweet."""
	feed = feedparser.parse(url)
	if feed:
		for item in feed["items"]:
			link = item["link"]
			permalink = item["guid"]
			if is_in_logfile(permalink, Settings.PostedUrlsOutputFile):
				print("Already posted:", permalink)
			else:
				image = opengraph.OpenGraph(url=link)['image']
				post_tweet(message=compose_message(item, 'JA'), auth = auth.TwitterAuth)
				post_tweet(message=compose_message(item, 'JA'), auth = auth.TwitterAuthSobiraj)
				post_toot(message=compose_message(item, 'JA'))
				post_telegram(message=compose_message(item, 'JA'))
				post_discord(message=compose_message(item, None))
				write_to_logfile(permalink, Settings.PostedUrlsOutputFile)
				post_signal(compose_message(item, None) + '\nZum beenden, antworten Sie einfach mit "Stop".')
				print("Posted:", permalink)


def is_in_logfile(content, filename):
	"""Does the content exist on any line in the log file?"""
	if os.path.isfile(filename):
		with open(filename) as f:
			lines = f.readlines()
		if (content + "\n" or content) in lines:
			return True
	return False

def write_to_logfile(content, filename):
	"""Append content to log file, on one line."""
	try:
		with open(filename, "a") as f:
			f.write(content + "\n")
	except IOError as e:
		print(e)


if __name__ == "__main__":
	read_rss_and_tweet(url=Settings.FeedUrl)