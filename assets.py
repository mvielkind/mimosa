import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")


def create_sync_services():
	"""
	Creates the Twilio Sync Service / Map to track customer phone numbers and Trello card IDs. 
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	# Create the Twilio Sync Service.
	service = client.sync.services.create()
	service_sid = service.sid

	# Create a Sync Map for the service.
	sync_map = client.sync.services(service_sid) \
		.sync_maps \
		.create()

	return service_sid, sync_map.sid


def create_custom_fields():
	"""
	Add custom fields to the board for customer name and phone number.

	Having these custom fields will allow Trello to use these fields in the messages that are sent.
	"""
	url = "https://api.trello.com/1/customFields"

	headers = {
		"Accept": "application/json"
	}

	base_query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idModel': TRELLO_BOARD,
		'modelType': 'board',
		'type': 'text',
		'pos': 1,
		'display_cardFront': "false"
	}

	for f in ["name", "phone_number"]:
		base_query["name"] = f

		response = requests.request(
			"POST",
			url,
			headers=headers,
			params=base_query
		)

		print(json.loads(response.text))
