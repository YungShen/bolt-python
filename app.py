import os
import s3fs
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.basicConfig(level=logging.INFO)
# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Add functionality here


@app.command("/hello-socket-mode")
def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi <@{user_id}>!")


@app.command("/ls")
def ls_command(ack, respond, command):
    ack()
    logger.info(body)
    path = command['text'] if command['text'] else ""
    res = ",".join(s3fs.S3FileSystem().ls(f"bd-mpdw-dev-slack/{command['text']}"))

    respond(res)


@app.event("app_mention")
def event_test(event, say):
    say(f"Hi there, <@{event['user']}>!")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # Call views.publish with the built-in client
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            # Home tabs must be enabled in your app configuration
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome home, <@" + event["user"] + "> :house:*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                          "type": "mrkdwn",
                          "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>."
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


def ack_shortcut(ack):
    ack()


def open_modal(body, client):
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "socket_modal_submission",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "title": {
                "type": "plain_text",
                "text": "Socket Modal",
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "q1",
                    "label": {
                        "type": "plain_text",
                        "text": "Write anything here!",
                    },
                    "element": {
                        "action_id": "feedback",
                        "type": "plain_text_input",
                    },
                },
                {
                    "type": "input",
                    "block_id": "q2",
                    "label": {
                        "type": "plain_text",
                        "text": "Can you tell us your favorites?",
                    },
                    "element": {
                        "type": "external_select",
                        "action_id": "favorite-animal",
                        "min_query_length": 0,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select your favorites",
                        },
                    },
                },
            ],
        },
    )


app.shortcut("socket-mode")(ack=ack_shortcut, lazy=[open_modal])


all_options = [
    {
        "text": {"type": "plain_text", "text": ":cat: Cat"},
        "value": "cat",
    },
    {
        "text": {"type": "plain_text", "text": ":dog: Dog"},
        "value": "dog",
    },
    {
        "text": {"type": "plain_text", "text": ":bear: Bear"},
        "value": "bear",
    },
]


@app.options("favorite-animal")
def external_data_source_handler(ack, body):
    keyword = body.get("value")
    if keyword is not None and len(keyword) > 0:
        options = [o for o in all_options if keyword in o["text"]["text"]]
        ack(options=options)
    else:
        ack(options=all_options)


@app.view("socket_modal_submission")
def submission(ack):
    ack()


if __name__ == "__main__":
    # Create an app-level token with connections:write scope
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
