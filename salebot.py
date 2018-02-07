#!/usr/bin/env python3

from slackclient import SlackClient
import configparser
import praw, time, sqlite3, re

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
CONSOLE_LOG = config["General"]["consolelog"]

sc = SlackClient(SLACK_TOKEN)

conn = sqlite3.connect("salebot.db")
c = conn.cursor()

reddit = praw.Reddit(user_agent="Test reddit parser", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

try:
	c.execute("CREATE TABLE posts (subreddit text, id text)")
	conn.commit()
except sqlite3.OperationalError:
	pass #If the table already exists do nothing

def printlog(message):
	if CONSOLE_LOG.lower() == "true": #python is kinda weird about string bools
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

while True:
	printlog("Searching subreddits for new deals . . .")
	for subname in config["Subreddits"]:
		printlog("Searching sub: " + subname)
		for submission in reddit.subreddit(subname).new(limit=int(POST_LIMIT)):
			c.execute("SELECT * FROM posts WHERE subreddit=? AND id=?", [subname, submission.id])
			if c.fetchone():
				break
			c.execute("INSERT INTO posts (subreddit, id) VALUES (?, ?)", [subname, submission.id])
			conn.commit()
			if scanSubmission(submission, REGEX):
				sendNotification(submission, subname)
				printlog("Sent notification for submission: " + submission.id)
	time.sleep(SLEEP_TIME)
	