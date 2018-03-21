#!/usr/bin/env python3

from slackclient import SlackClient
import configparser
import praw, time, re

config = configparser.ConfigParser(allow_no_value=True)

config.read("settings.ini")
SLACK_TOKEN = config["SlackAccount"]["token"]
USERNAME = config["SlackAccount"]["username"]
USER_ICON = config["SlackAccount"]["icon"]
USER_CHANNEL = config["SlackAccount"]["channel"]

CLIENT_ID = config["RedditAccount"]["client_id"]
CLIENT_SECRET = config["RedditAccount"]["client_secret"]

SLEEP_TIME = int(config["General"]["sleep"])
REGEX = config["General"]["regex"]
POST_LIMIT = config["General"]["postlimit"]
CONSOLE_LOG = "consolelog" in config["General"]

LASTRUN = config["Data"]["lastrun"]

sc = SlackClient(SLACK_TOKEN)

reddit = praw.Reddit(user_agent="Test reddit parser", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def printlog(message):
	if CONSOLE_LOG:
		print(message)

def pushNotify(message):
	sc.api_call(
	"chat.postMessage",
	channel=USER_CHANNEL,
	username=USERNAME,
	icon_emoji=USER_ICON,
	text=message
	)

def sendNotification(submission, subname):
	string = ""
	string += submission.title + "\n"
	string += "Subreddit: " + subname + "\n"
	string += "https://www.reddit.com/r/" + subname + "/comments/" + submission.id + "/"
	pushNotify(string)

def scanSubmission(submission, regex):
	match = re.search(regex, submission.title, re.I)
	if match:
		return True
	else:
		return False

breakLoop = "noloop" in config["General"]

while True:
	printlog("Searching subreddits for new deals . . .")
	startTime = time.time()
	for subname in config["Subreddits"]:
		printlog("Searching sub: " + subname)
		for submission in reddit.subreddit(subname).new(limit=int(POST_LIMIT)):
			print(submission.created_utc, ":", LASTRUN)
			if submission.created_utc < float(LASTRUN):
				break
			if scanSubmission(submission, REGEX):
				sendNotification(submission, subname)
				printlog("Sent notification for submission: " + submission.id)
	LASTRUN = startTime
	config["Data"]["lastrun"] = str(startTime)
	with open('settings.ini', 'wb') as configfile:
		config.write(configfile)
	if breakLoop:
		break
	time.sleep(SLEEP_TIME)
	
printlog("Done.")