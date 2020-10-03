import os
import json
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = os.getenv("TRELLO_BOARD_ID")
TRELLO_WAITLIST_ID = os.getenv("TRELLO_WAITLIST_ID")

TRELLO_FIELDS = {
	"name": "5f75c09969ea425523bfc858",
	"phone_number": "5f75c0993f480350c397b27f"
}

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SYNC_SERVICE = "IS9b10209df6ad4070ab178da3b6b233d5"
TWILIO_SYNC_MAP = "MPc5a6752fc316499d83e462ccbb056af3"


def get_customer_card_id(phone_number):
	"""
	Check the Sync Map to see if there is a Card ID associated with the customer.
	"""	
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	try:
		card = client.sync \
			.services(TWILIO_SYNC_SERVICE) \
			.sync_maps(TWILIO_SYNC_MAP) \
			.sync_map_items(phone_number) \
			.fetch()

		return True
	except TwilioRestException as e:
		return False


def create_card_in_waitlist(title, desc, phone_number):
	"""
	Create a new customer card in the waitlist.
	"""
	url = "https://api.trello.com/1/cards"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'idList': TRELLO_WAITLIST_ID,
		'name': title,
		'desc': desc
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)

	# Create an entry in the Sync Map for the newly created card.
	card_id = json.loads(response.text)["id"]
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	card = client.sync \
		.services(TWILIO_SYNC_SERVICE) \
		.sync_maps(TWILIO_SYNC_MAP) \
		.sync_map_items \
		.create(
			key=phone_number,
			data={
				'card_id': card_id
			}
		)

	return response


def update_card_custom_fields(card_id, field_name, value):
	custom_field_id = TRELLO_FIELDS[field_name]

	url = f"https://api.trello.com/1/cards/{card_id}/customField/{custom_field_id}/item"
	
	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'modelType': 'card',
		'value': {
			'text': value
		}
	}

	response = requests.request(
   		"PUT",
   		url,
   		json=query
	)

	return response


def get_lists_on_board():
	"""
	Get all the of the lists on a board.

	returns: a list of all the lists that are included on the board.
	"""
	url = f"https://api.trello.com/1/boards/{TRELLO_BOARD}/lists"

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN
	}

	response = requests.request(
		"GET",
		url,
		params=query
	)

	return json.loads(response.text)


def add_attachment_to_card(card_id):
	url = f"https://api.trello.com/1/cards/{card_id}/attachments"

	headers = {
 	  "Accept": "application/json"
	}

	query = {
		'key': TRELLO_API_KEY,
		'token': TRELLO_TOKEN,
		'url': "https://www.theyoungfolks.com/wp-content/uploads/2016/06/Marlin-and-Nemo.jpg"
	}

	response = requests.request(
		"POST",
		url,
		params=query
	)
