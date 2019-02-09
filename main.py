import os
import time
import re
from slackclient import SlackClient
import configparser

#OAUTH session allows you do more than just see messages, Namely delete messages
config = configparser.ConfigParser()
config.read('auth.ini')
sc = SlackClient(config.get('slack', 'OAuthAccessToken'),
                 client_id=config.get('slack', 'clientID'),
                 client_secret=config.get('slack', 'clientSecret')
                 )
#Real time message stream
sc_rtm = SlackClient(config.get('slack', 'BotUserOAuthAccessToken'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
channels = sc_rtm.api_call("users.list")

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event is not []:
            print(event)
        if event["type"] == "message" and 'thread_ts' not in event.keys() and 'text' in event.keys():
            if 'message' in event.keys() and 'is_thread_broadcast' in event['message'].keys() and event['message']['is_thread_broadcast'] == True:
                return sc.api_call(
                    "chat.delete",
                    channel=event['channel'],
                    ts=event['ts'],
                    as_user=True
                )
            print("is message")
            authorized_users = ['UF4BSTFFA','UF2EWT73N','UF52HLVS7','UF512Q91R','UF5A9PD25','UF6FUDVBQ']
            if event['user'] not in authorized_users and event['channel'] == 'CF2R9G613':
                print('USER NOT AUTHORIZED')
                return sc.api_call(
                    "chat.delete",
                    channel=event['channel'],
                    ts=event['ts'],
                    as_user=True
                )
            else:
                print('User is authorized. Ignoring')

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
    Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if sc_rtm.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = sc.api_call("auth.test")["user_id"]
        while True:
            response = parse_bot_commands(sc_rtm.rtm_read())
            if response is None:
                pass
            else:
                print(response)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")