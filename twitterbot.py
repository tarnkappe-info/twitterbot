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

class Settings:
	FeedUrl = "https://tarnkappe.info/feed/"    
	PostedUrlsOutputFile = "/root/twitter/posted-urls.log"

class TwitterAuth:
	"""
	Twitter authentication settings.

	Create a Twitter app at https://apps.twitter.com/ and generate key, secret etc. and insert them here.
	"""
	ConsumerKey = "xx"
	ConsumerSecret = "xx"
	AccessToken = "xx"
	AccessTokenSecret = "x"


class TwitterAuthSobiraj:
	"""
	Twitter authentication settings.

	Create a Twitter app at https://apps.twitter.com/ and generate key, secret etc. and insert them here.
	"""
	ConsumerKey = "xx"
	ConsumerSecret = "xx"
	AccessToken = "xx"
	AccessTokenSecret = "xx"


def compose_message(rss_item):
	"""Compose a tweet from title, link, and description, and then return the final tweet message."""
	title, link, description = rss_item["title"], rss_item["link"], rss_item["description"]
	tags = [t.term.replace(" ", "").replace("-", "").replace(".", "") for t in rss_item.get('tags', [])]
	categories_string = " #".join(tags)
	categories_string = "#" + categories_string
	message = "📬 Neuer Artikel 📬 " + shorten_text(title, maxlength=250) + " "+ str(categories_string) + " " + link
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

def read_rss_and_tweet(url):
	"""Read RSS and post tweet."""
	feed = feedparser.parse(url)
	if feed:
		for item in feed["items"]:
			link = item["link"]
			if is_in_logfile(link, Settings.PostedUrlsOutputFile):
				print("Already posted:", link)
			else:
				post_tweet(message = compose_message(item), auth = TwitterAuth)
				post_tweet(message = compose_message(item), auth = TwitterAuthSobiraj)
				write_to_logfile(link, Settings.PostedUrlsOutputFile)
				print("Posted:", link)


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
