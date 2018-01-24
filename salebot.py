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

sc = SlackClient(SLACK_TOKEN)

def pushNotify(message):
	sc.api_call(
	"chat.postMessage",
	channel=USER_CHANNEL,
	username=USERNAME,
	icon_emoji=USER_ICON,
	text=message
	)

def scanSubmission(submission, regex):
	match = re.search(regex, submission.title, re.I)
	if match:
		return True
	else:
		return False

reddit = praw.Reddit(user_agent="Test reddit parser", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

print(reddit.read_only)

readTitles = []

while True:
	print("START!")
	for subname in config["Subreddits"]:
		print("Searching sub: " + subname)
		for submission in reddit.subreddit(subname).new(limit=10):
			if submission.id in readTitles:
				break
			readTitles.append(submission.id)
			if scanSubmission(submission, REGEX):
				print(submission.title)
	time.sleep(SLEEP_TIME)