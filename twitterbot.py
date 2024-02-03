#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grequests
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
import json
from discord_webhook import DiscordWebhook
import auth
import opengraph
import base64
from PIL import Image
import io
import requests
from pyfacebook import GraphAPI
import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText
import tweepy


class Settings:
	FeedUrl = "https://tarnkappe.info/feed"
	PostedUrlsOutputFile = "/root/twitter/posted-urls.log"


def compose_message(rss_item, with_cats, with_link):
	"""Compose a tweet from title, link, and description, and then return the final tweet message."""
	title, link, description = rss_item["title"], rss_item["link"], rss_item["description"]
	tags = [t.term.replace(" ", "").replace("-", "").replace(".", "").replace("&", "").replace(":", "").replace(":", "").replace("/", " #").replace("(", "").replace(")", "").replace("$", "").replace("#", "") for t in rss_item.get('tags', [])]
	categories_string = " #".join(tags)
	categories_string = "#" + categories_string
	message = "📬 " + shorten_text(title, maxlength=240) + "\n"
	if with_cats:
		message += str(categories_string) + " "
	if with_link:
		message += create_shortlink(link)
	return message

def shorten_text(text, maxlength):
	"""Truncate text and append three dots (...) at the end if length exceeds maxlength chars."""
	return (text[:maxlength] + '...') if len(text) > maxlength else text

def post_tweet(message, auth):
	"""Post tweet message to account."""
	try:
		twitter = tweepy.Client(consumer_key=auth.ConsumerKey, consumer_secret=auth.ConsumerSecret, access_token=auth.AccessToken, access_token_secret=auth.AccessTokenSecret)
		twitter.create_tweet(text=message, user_auth=True)
	except Exception as e:
		print(e)

def create_shortlink(url):
	params = {"token_auth": auth.Matomo.authtoken, "tokenAuth": auth.Matomo.authtoken, "useExistingCodeIfAvailable": 0, "force_api_session": 1, "url": str(url)}
	response = dict(requests.post(auth.Matomo.url, params=params).json())
	return "https://sc.tarnkappe.info/"+response["value"]


def post_telegram(message):
	params = {"chat_id": auth.TelegramAuth.ChatID, "text": message}
	url = f"https://api.telegram.org/bot{auth.TelegramAuth.Token}/sendMessage"
	requests.post(url, params=params)

def post_toot(message):
	try:
		mastodon = Mastodon(access_token=auth.MastodonAuth.access_token, api_base_url=auth.MastodonAuth.api_base_url)
		mastodon.toot(message)
	except mastodon as e:
		print(e)

def stop_signal(number):
	newfile = []
	with open("/root/Signal/rss/numbers.txt") as file:
		for line in file:
			if line.rstrip() == number:
				continue
			else:
				newfile.append(line)
	file_object = open('/root/Signal/rss/numbers.txt', 'w')
	file_object.writelines(newfile)
	file_object.close()


def post_signal(message, image):
	if image:
		img = Image.open(io.BytesIO(requests.get(image, stream=True).content))
		img.thumbnail((900, 900))
		with io.BytesIO() as output:
			img.save(output, format="PNG")
			base64data = [str(base64.b64encode(output.getvalue()).decode('utf-8'))]
	with open("/root/Signal/rss/numbers.txt") as file:
		rs = list()
		for line in file:
			data = {"message": message, "number": "+4917677918637", "recipients": [ line.rstrip() ], 'base64_attachments': base64data}
			rs.append(grequests.post('http://127.0.0.1:8120/v2/send/', timeout=600, json=data))
		for resp in grequests.imap(rs, size=5):
			if resp.status_code is 400:
				stop_signal(str(json.loads(resp.request.body)["number"]))

def post_facebook(message, url):
	fbapi = GraphAPI(access_token = auth.FbGraphAPI.access_token)
	fbapi.post_object(object_id="1420074268248034", connection="feed", data={"message": message, "link": url})


def post_discord(message):
	webhook = DiscordWebhook(url='https://discord.com/api/webhooks/' + auth.DiscordAuth.webhook, content=message)
	response = webhook.execute()

async def post_matrix_async(message, roomid) -> None:
	matrixclient = AsyncClient("https://matrix.tarnkappe.info", "@tk_matrixbot:tarnkappe.info")
	matrixclient.access_token = auth.Matrix.access_token
	await matrixclient.room_send(
		room_id=roomid,
		content={"msgtype": "m.text", "body": message},
		message_type="m.room.message")
	await matrixclient.close()

def post_matrix(message, roomid):
	asyncio.get_event_loop().run_until_complete(post_matrix_async(message, roomid))

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
				write_to_logfile(permalink, Settings.PostedUrlsOutputFile)
				try:
					post_tweet(message=compose_message(item, 'JA', with_link="YES"), auth = auth.TwitterAuth)
					post_tweet(message=compose_message(item, 'JA', with_link="YES"), auth = auth.TwitterAuthSobiraj)
				except:
					pass
				try:
					post_toot(message=compose_message(item, 'JA', with_link="YES"))
					post_telegram(message=compose_message(item, 'JA', with_link="YES"))
					post_discord(message=compose_message(item, None, with_link="YES"))
					post_facebook(message=compose_message(item, 'JA', None), url=link)
				except:
					pass
				try:
					post_matrix(message=compose_message(item, None, with_link="YES"), roomid='!pfwAegfuzkCMNTJkVf:tarnkappe.info')
					#post_matrix(message=compose_message(item, None, with_link="YES"), roomid='!y1ahUxHPrBTs6lnf:tarnkappe.info')
					#post_matrix(message=compose_message(item, None, with_link="YES"), roomid='!ZSgw1Y1VAlHtfVsR:tarnkappe.info')
				except:
					pass
				try:
					post_signal(compose_message(item, None, with_link="YES"), image)
				except:
					pass 
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