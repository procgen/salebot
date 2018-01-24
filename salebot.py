from slackclient import SlackClient
import configparser

config = configparser.ConfigParser()

config.read("settings.ini")
SLACK_TOKEN = config["SlackAccount"]["token"]
USERNAME = config["SlackAccount"]["username"]
USER_ICON = config["SlackAccount"]["icon"]
USER_CHANNEL = config["SlackAccount"]["channel"]

sc = SlackClient(SLACK_TOKEN)

def pushNotify(message):
	sc.api_call(
	"chat.postMessage",
	channel=USER_CHANNEL,
	username=USERNAME,
	icon_emoji=USER_ICON,
	text=message
	)

pushNotify("Post generic message")