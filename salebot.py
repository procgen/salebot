from slackclient import SlackClient
import configparser
import praw, time, sqlite3

config = configparser.ConfigParser()

config.read("settings.ini")
SLACK_TOKEN = config["SlackAccount"]["token"]
USERNAME = config["SlackAccount"]["username"]
USER_ICON = config["SlackAccount"]["icon"]
USER_CHANNEL = config["SlackAccount"]["channel"]

CLIENT_ID = config["RedditAccount"]["client_id"]
CLIENT_SECRET = config["RedditAccount"]["client_secret"]

sc = SlackClient(SLACK_TOKEN)

def pushNotify(message):
	sc.api_call(
	"chat.postMessage",
	channel=USER_CHANNEL,
	username=USERNAME,
	icon_emoji=USER_ICON,
	text=message
	)

#pushNotify("Post generic message")
reddit = praw.Reddit(user_agent="Test reddit parser", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

print(reddit.read_only)

readTitles = []

subreddit = reddit.subreddit("GameDeals")
while True:
	print("START!")
	for submission in subreddit.new(limit=10):
		if submission.id in readTitles:
			break
		readTitles.append(submission.id)
		print("-----------")
		print(submission.title)
		print(submission.url)
		print(submission.id)
		print("-----------")
	time.sleep(10)