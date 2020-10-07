import os
import json
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv
load_dotenv()


TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_BOARD = "5f7312a009963d58f67798cd"
TRELLO_WAITLIST_ID = "5f731c76dcdc6e64abcd472f"
TRELLO_LISTS = {
	"Waitlist": "5f731c76dcdc6e64abcd472f",
	"Cancellations": "5f731cbcfeff7640ed977775"
}
TRELLO_FIELDS = {
	"name": "5f75c09969ea425523bfc858",
	"phone_number": "5f75c0993f480350c397b27f"
}
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SYNC_SERVICE = 'IS64c852fe6f8101aacfa6be27bc7823ca'
TWILIO_SYNC_MAP = 'MP0ccdd2257c7a41e7a3fa39b3f728e850'


def check_if_card_exists(phone_number):
	"""
	"""
	card_id = get_trello_card_id(phone_number)

	if card_id:
		return True
	else:
		return False


def get_trello_card_id(phone_number):
	"""
	Gets the Trello Card ID for a phone number.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	try:
		response = client.sync \
			.services(TWILIO_SYNC_SERVICE) \
			.sync_maps(TWILIO_SYNC_MAP) \
			.sync_map_items(phone_number) \
			.fetch()
	except TwilioRestException:
		return None

	return response


def remove_customer_from_sync_map(phone_number):
	"""
	Removes the Sync Map item for the customer.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	sync_map_item = client.sync \
		.services(TWILIO_SYNC_SERVICE) \
		.sync_maps(TWILIO_SYNC_MAP) \
		.sync_map_items(phone_number) \
		.delete()

	return sync_map_item


def add_customer_to_sync_map(phone_number, card_id):
	"""
	Adds a new customer entry to the Sync Map.
	"""
	client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

	sync_map_item = client.sync \
		.services(TWILIO_SYNC_SERVICE) \
		.sync_maps(TWILIO_SYNC_MAP) \
		.sync_map_items \
		.create(key=phone_number, data={
			"trello_card_id": card_id
		})

	return sync_map_item


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

	card_id = json.loads(response.text)["id"]

	# Create the Sync Map entry for phone number.
	sync_item = add_customer_to_sync_map(phone_number, card_id)

	return response


def update_card_list(card_id, new_list):
	"""
	Assign a card to a new list.
	"""
	url = f"https://api.trello.com/1/cards/{card_id}"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'idList': TRELLO_LISTS[new_list]
	}

	response = requests.request(
	   "PUT",
	   url,
	   headers=headers,
	   json=query
	)

	return response


def get_lists_on_board():
	"""
	Get all the of the lists on a board.
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

	return response.text


def update_custom_fields(card_id, field_name, value):
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


def create_custom_fields():
	"""
	"""
	url = "https://api.trello.com/1/customFields"

	headers = {
	   "Accept": "application/json"
	}

	query = {
	   'key': TRELLO_API_KEY,
	   'token': TRELLO_TOKEN,
	   'idModel': TRELLO_BOARD,
	   'modelType': 'board',
	   'type': 'text',
	   'pos': 1,
	   'display_cardFront': 'false'
	}

	for f in ["name", "phone_number"]:
		query["name"] = f

		response = requests.request(
		   "POST",
		   url,
		   headers=headers,
		   params=query
		)

		print(json.loads(response.text))
