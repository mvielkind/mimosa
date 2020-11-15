import os
import click
import requests
import json
import trello
from twilio.rest import Client
import dotenv
dotenv.load_dotenv()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER_SID = os.getenv("TWILIO_PHONE_NUMBER_SID")
TWILIO_AUTOPILOT_SID = os.getenv("TWILIO_AUTOPILOT_SID")

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("board_name")
@click.argument("ngrok_url")
def deploy(board_name, ngrok_url):
	"""
	Create all of the Trello board assets.
	"""
	# Create Trello Board.
	#board = create_trello_board(board_name)
	#board_id = board["id"]
	board_id = "5fae7fe5a4f4854d4898883f"
	dotenv.set_key(".env", "TRELLO_BOARD_ID", board_id)

	# Enable Custom Fields Power-Up.
	powerup = enable_board_powerup(board_id, "56d5e249a98895a9797bebb9")

	# Create Trello lists.
	trello_lists = ["No Show", "Cancellations", "Completed", "Table is Ready", "Waitlist"]
	for l in trello_lists:
		create_trello_list(l, board_id)

	# Create the Trello labels.
	trello_labels = [
		{"label_name": "FirstNudge", "label_color": "green"},
		{"label_name": "SecondNudge", "label_color": "yellow"},
		{"label_name": "FinalNudge", "label_color": "red"},
		{"label_name": "unverified", "label_color": "blue"}
	]
	for lbl in trello_labels:
		create_trello_label(**lbl, board_id=board_id)

	# Create the custom fields.
	trello_fields = ["name", "phone_number"]
	for field in trello_fields:
		create_custom_fields(field, board_id)

	# Setup the Twilio Sync Service.
	sync_service, sync_map = create_sync_services()

	# Create the Twilio Studio Flow.
	flow = create_studio_flow(ngrok_url)

	# Add flow to the our phone number.
	phone = update_phone_incoming_webhook(flow.webhook_url)


@cli.command()
@click.argument("ngrok_url")
def update_autopilot_endpoints(ngrok_url):
	"""
	Replace the NGROK_URL placeholders in the Autopilot schema_template.json file with the valid ngrok URL.

	Writes output to a file schema.json that can be used to create or update your Autopilot bot.
	"""
	# Read the schema template.
	schema_template = json.dumps(json.load(open("schema_template.json", "r")))

	# Replace the <NGROK_URL> occurrences.
	new_schema = json.loads(schema_template.replace("<NGROK_URL>", ngrok_url))

	json.dump(new_schema, open("schema.json", "w"))


def create_studio_flow(ngrok_url):
	"""
	Reads the flow_template.json file and makes replacements in the template for the proper Autopilot SID
	and the NGROK URL being used.

	New definition is used to create the Twilio Studio Flow. If the Studio flow exists then the existing Flow
	will be updated using the new Studio Flow template.
	"""
	# Read and make replacements.
	flow_def = json.dumps(json.load(open("flow_template.json", "r"))).\
		replace("<AUTOPILOT_SID>", TWILIO_AUTOPILOT_SID).\
		replace("<NGROK_URL>", ngrok_url)

	# Convert to a dictionary representation.
	flow_def = json.loads(flow_def)

	# Check if the Studio Flow already exists.
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	flow_sid = os.getenv("TWILIO_FLOW_SID")
	if flow_sid == "":
		# Create the flow with the Twilio API.
		flow = client.studio.flows.create(
			commit_message='First draft',
			friendly_name='mimosa',
			status='published',
			definition=flow_def)

		# Write Flow SID to the environmental file.
		dotenv.set_key(".env", "TWILIO_FLOW_SID", flow.sid)
	else:
		# Update the existing Studio Flow.
		flow = client.studio.flows(flow_sid).update(
			commit_message='Push flow update.',
			status='published',
			definition=flow_def
		)

	return flow


def update_phone_incoming_webhook(flow_webhook):
	"""
	Connects the Twilio Studio Flow to your Twilio phone number.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	phone = client.incoming_phone_numbers(TWILIO_PHONE_NUMBER_SID).\
		update(
			sms_url=flow_webhook
		)

	return phone


def create_sync_services():
	"""
	Create the Twilio Sync Service and the Sync Map to track customer phone numbers and the Trello card IDs.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	# Create the sync service.
	service = client.sync.services.create(friendly_name='mimosa')
	response = dotenv.set_key(".env", "TWILIO_SYNC_SID", service.sid)

	# Create the Sync Map.
	sync_map = client.sync.services(service.sid) \
		.sync_maps \
		.create()

	response = dotenv.set_key(".env", "TWILIO_SYNC_MAP_SID", sync_map.sid)

	return service.sid, sync_map.sid


def create_trello_board(board_name):
	"""
	Creates a blank Trello Board.
	"""
	url = "https://api.trello.com/1/boards/"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'name': board_name,
		'defaultLists': "false",
		'defaultLabels': "false"
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	return json.loads(response.text)


def enable_board_powerup(board_id, plugin_id):
	url = f"https://api.trello.com/1/boards/{board_id}/boardPlugins"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idPlugin': plugin_id
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	print(response.text)


def create_trello_label(label_name, label_color, board_id):
	"""
	Create a Trello label for the board.
	"""
	url = "https://api.trello.com/1/labels"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'name': label_name,
		'color': label_color,
		'idBoard': board_id
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	print(response.text)


def create_trello_list(list_name, board_id):
	# Check if list exists.
	list_id = trello.get_list_id(list_name)
	if list_id:
		print(f"List {list_name} already exists")
	else:
		url = "https://api.trello.com/1/lists"

		query = {
			'key': TRELLO_API_KEY,
			'token': TRELLO_TOKEN,
			'name': list_name,
			'idBoard': board_id
		}

		response = requests.request(
			"POST",
			url,
			params=query
		)

		print(response.text)


def create_custom_fields(field_name, board_id):
	"""
	"""
	url = "https://api.trello.com/1/customFields"

	headers = {
		"Accept": "application/json"
	}

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idModel': board_id,
		'modelType': 'board',
		'type': 'text',
		'pos': 1,
		'name': field_name,
		'display_cardFront': 'false'
	}

	response = requests.request(
		"POST",
		url,
		headers=headers,
		params=query
	)

	print(response.text)


if __name__ == "__main__":
	cli()
